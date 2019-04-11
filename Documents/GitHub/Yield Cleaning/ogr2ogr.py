# -*- coding: utf-8 -*-
"""
ogr2ogr - yield cleaning problem 

Created on Thu Apr 11 10:36:36 2019

@author: lmlev
"""

from osgeo import ogr
from osgeo import osr
import os, sys

def main(attribute):
    #Get the input layer
    inShapefile = r'C:\Users\lmlev\Dropbox\Classes\Spring 2019\GIS 5541\Projects\soy_yield.shp'
    inDriver = ogr.GetDriverByName("ESRI Shapefile")
    inDataSource = inDriver.Open(inShapefile, 0)
    inLayer = inDataSource.GetLayer()
    inLayer.SetAttributeFilter(attribute)
    
    #Create the output layers 
    outShapefile = os.path.join(os.path.split(inShapefile)[0], "ogr_api_filter8.shp")
    outDriver = ogr.GetDriverByName("ESRI Shapefile")
    
    #Remove output shapefile if it already exists
    if os.path.exists(outShapefile):
        outDriver.DeleteDataSource(outShapefile)
        
    # Create the output shapefile 
    outDataSource = outDriver.CreateDataSource(outShapefile)
    out_lyr_name = os.path.splitext(os.path.split(outShapefile)[1])[0]
    
    in_srs = osr.SpatialReference()
    in_srs.ImportFromEPSG(4326)
    outLayer = outDataSource.CreateLayer(out_lyr_name, geom_type=ogr.wkbPoint, srs=in_srs)
#    outLayer = outDataSource.CreateLayer(out_lyr_name, geom_type=ogr.wkbPoint)
    
    print(outLayer.GetSpatialRef())

    # Add input Layer Fields to the output Layer if it is the one we want 
    inLayerDefn = inLayer.GetLayerDefn()
    for i in range(0, inLayerDefn.GetFieldCount()):
        fieldDefn = inLayerDefn.GetFieldDefn(i)
        fieldName = fieldDefn.GetName()
        outLayer.CreateField(fieldDefn)
        
    # Get the output Layer's Feature Definition
    outLayerDefn = outLayer.GetLayerDefn()
    
    #Add Features to the output layer
    for inFeature in inLayer:
        outFeature = ogr.Feature(outLayerDefn)
        
        # Add field values from input Layer 
        for i in range(0, inLayerDefn.GetFieldCount()):
#        for i in range(0, outLayerDefn.GetFieldCount()):
            fieldDefn = inLayerDefn.GetFieldDefn(i)
            fieldName = fieldDefn.GetName()
#            print(fieldName)
#            print(inFeature.GetField(i))
#            fieldDefn_out = outLayerDefn.GetFieldDefn(i)
            outFeature.SetField(outLayerDefn.GetFieldDefn(i).GetNameRef(), inFeature.GetField(i))
            
#            outFeature.SetField(fieldName, inFeature.GetField(i))
#        if idx > 2:
#            break
#            if fieldName not in field_name_target:
#                continue
            
        # Set geometry 
        geom = inFeature.GetGeometryRef()
        outFeature.SetGeometry(geom.Clone())
        #Add new feature to output layer
        outLayer.CreateFeature(outFeature)
        outFeature = None
        
    #Save and Close 
    inDataSource = None
    outDataSource = None
    
main("Swth_Wdth_ = 30")
