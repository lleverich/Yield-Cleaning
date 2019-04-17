# -*- coding: utf-8 -*-
"""
Created on Tue Dec 18 00:07:41 2018

@author: nigo0024
"""
import pandas as pd
import math
import os

import seaborn as sns
import numpy as np
from sklearn import preprocessing
import matplotlib.pyplot as plt

class Flow_shift(object):
    '''
    Functions for processing yield monitor data
    '''
    def __init__(self, fname_in=None):
        self.fname_in = fname_in

    def _mph_to_mps(self, mph):
        '''Converts miles per hour to meters per second'''
        return mph * 0.44704

    def _shift_distance(self, heading, speed, x, y, shift_sec):
        '''Shifts x and y for a given point'''
        mps = self._mph_to_mps(speed)
        radius = shift_sec * mps  # distance points should move
        heading2 = ((heading - 270) + 360) % 360
        head_rad = math.radians(heading2)
        x_new = x - (radius * math.cos(head_rad))
        y_new = y + (radius * math.sin(head_rad))
        return x_new, y_new

    def _get_outname(self, fname_in, append='_out', ext_out=None):
        '''Creates output name from input name'''
        dirname, name = os.path.split(fname_in)
        name, ext = os.path.splitext(name)
        if append is None:
            append = ''
        if ext_out is None:
            ext_out = ext
        return os.path.join(dirname, name + append + ext_out)

    def flow_shift(self, fname_in, shift_sec=2, append='_flowshift',
                   head_x='xcoord', head_y='ycoord'):
        '''
        Shifts grain flow readings based on "heading", "speed", and <shift_sec>
        '''
        fname_out_flowshift = self._get_outname(fname_in, append=append)
        df = pd.read_csv(fname_in)

        for idx, row in df.iterrows():
            x_new, y_new = self._shift_distance(row.heading, row.speed,
                                                row[head_x], row[head_y],
                                                shift_sec)
            df.at[idx, [head_x, head_y]] = [x_new, y_new]
        df.to_csv(fname_out_flowshift)

    def csv_to_agleader_advanced(self, fname_csv, head_x='xcoord',
                                 head_y='ycoord', grain_type='CORN'):
        '''
        Converts a csv file into a .txt file with "AgLeader Advanced"
        formatting

        See: https://support.agleader.com/kbp/index.php?View=entry&EntryID=1942

        <fname_csv> must have the following columns (with the same names):
            1. 'ycoord' (<head_y> supports any other heading names)
            2. 'xcoord' (<head_x> supports any other heading names)
            3. 'mass_corn'
            4. 'timestamp' (i.e., GPS time)
            5. 'duration' (i.e., logging interval)
            6. 'distance'
            7. 'width' (i.e., swath)
            8. 'moisture'
            14. 'grain_type' (not required; choose via <grain_type> variable)
            17. 'elevation' (i.e., altitude)


        These columns are not required (and not supported):
            9. 'Header Status'
            10. 'Pass'
            11. 'Serial Number'
            12. 'Field ID'
            13. 'Load ID'
            15. 'GPS Status'
            16. 'PDOP'

        '''
        fname_out = self._get_outname(fname_csv, append=None, ext_out='.txt')
        cols_required = [head_x, head_y, 'mass_corn', 'timestamp', 'duration',
                         'distance', 'width', 'moisture', 'elevation']
        cols_ordered = [head_x, head_y, 'mass_corn', 'timestamp', 'duration',
                        'distance', 'width', 'moisture', 'header_status',
                        'pass', 'ser_number', 'field_id', 'load_id',
                        'grain_type', 'gps_status', 'pdop', 'elevation']
        df = pd.read_csv(fname_csv)
        df_new = df[cols_required].copy()
        df_new['header_status'] = 33
        df_new['pass'] = 0
        df_new['ser_number'] = 'NOMONITOR'
        df_new['field_id'] = 'NONE'
        df_new['load_id'] = 'NONE'
        df_new['grain_type'] = grain_type
        df_new['gps_status'] = 7
        df_new['pdop'] = 0

        df_new = df_new[cols_ordered]
        df_new.to_csv(fname_out, header=False, index=False)

    def _standardize_val(self, pfit, x, y, avg_val=100):
        '''
        Standardizes an arbitrary data value using a numpy.poly1d convenience
        class <pfit> given the x value <x> and y value <y>
        See: https://docs.scipy.org/doc/numpy-1.15.1/reference/generated/numpy.poly1d.html
        '''
        coef = pfit(x) / avg_val
        yield_std = y / coef
        return yield_std

    def plot(self, df, pfit=None, col_x='dem_elev', col_y='dry_yield',
             hue=None, ax=None):
        '''Plots a scatterplot with a polyfit line'''
        sns.scatterplot(x=col_x, y=col_y, hue=hue,
                        data=df, s=12, ax=ax)
        if pfit is not None:
            xp = np.linspace(df[col_x].min(), df[col_x].max(), 100)
            _ = ax.plot(xp, pfit(xp), '-k')

    def normalize_yield(self, fname_in, col_elev='dem_elev',
                        col_yield='dry_yield', poly_deg=3, append='_yieldnorm',
                        plot=True, hue=None):
        '''
        Normalizes the yield dataset by generating a polynomial fit between
        elevation and yield
        '''
        fname_out = self._get_outname(fname_in, append=append)
        df = pd.read_csv(fname_in)
        z = np.polyfit(x=df[col_elev], y=df[col_yield], deg=poly_deg)
        pfit = np.poly1d(z)

        yield_avg = df[col_yield].mean()
        print(yield_avg)

        yield_std = self._standardize_val(
                pfit, df[col_elev], df[col_yield], avg_val=yield_avg)
        yield_norm = (yield_std - yield_std.min()) / (yield_std.max() -
                      yield_std.min())
#        yield_norm2 = (yield_std - yield_std.min()) / (yield_std.max() -
#                      yield_std.min())

        df['dry_yield_norm'] = yield_norm
        df.to_csv(fname_out, index=False)

        if plot is True:
            fig, (ax1, ax2) = plt.subplots(nrows=2)
            self.plot(df, pfit, col_x=col_elev, col_y=col_yield, hue=hue, ax=ax1)
            sns.scatterplot(x=col_elev, y='dry_yield_norm', hue=hue,
                            data=df, s=12, ax=ax2)
        return df