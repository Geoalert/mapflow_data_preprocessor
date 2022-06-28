from osgeo import gdal, osr
import argparse
import math
import os
import logging
import datetime
import os


def main(input_tif, output_tif, pixel_size, dst_crs):
    """If user projection is "None" - use projection "3857", and calculate pixel size in 'real meter'."""
    if dst_crs is None:
        dst_crs = '3857'
        pixel_size = calculate_res_from_gsd(input_tif, pixel_size)

    gdal.Warp(output_tif, input_tif, xRes=pixel_size, yRes=pixel_size, dstSRS='EPSG:' + dst_crs)
    print('End resample. Result:', output_tif)


def calculate_res_from_gsd(input_tif, pixel_size):
    # open tif
    dataset = gdal.Open(input_tif)
    # get center rastr
    xmin, ymin, xmax, ymax = get_extent(dataset)
    center = [(xmin + xmax) / 2, (ymin + ymax) / 2]
    # input SpatialReference
    proj = osr.SpatialReference(wkt=dataset.GetProjection())
    epsgid = int(proj.GetAttrValue('AUTHORITY', 1))
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(epsgid)
    # output SpatialReference
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(4326)
    # trasform  rastr cernter to EPSG:4326
    re_center = reproject_coords(center, src_srs=inSpatialRef, tgt_srs=outSpatialRef)
    # Get coefficient of real meter
    coef = math.cos(math.radians(re_center[0]))
    # change pixel size
    pixel_size = pixel_size * coef
    return pixel_size

def get_extent(ds):
    """Get extent of dataset raster"""
    xmin, xpixel, _, ymax, _, ypixel = ds.GetGeoTransform()
    width, height = ds.RasterXSize, ds.RasterYSize
    xmax = xmin + width * xpixel
    ymin = ymax + height * ypixel
    return xmin, ymin, xmax, ymax

def reproject_coords(coords,src_srs,tgt_srs):
    """Reprojection coordinates"""
    transform = osr.CoordinateTransformation(src_srs, tgt_srs)
    x, y, z = transform.TransformPoint(coords[0], coords[1])
    return x, y

if __name__ == "__main__":
    dir = os.path.dirname(os.path.abspath(__file__))
    logging.basicConfig(filename= dir + "/resample_mapflow.log", level=logging.INFO)
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('input_tif', type=str, help='input .tif file')
        parser.add_argument('output_tif', type=str, help='output .tif file')
        parser.add_argument('--pixel_size', type=float, help='pixel size in meter', default=0.8)
        parser.add_argument('--dst_crs', type=str, help='EPSG', default=None)
        args = parser.parse_args()
        logging.info(str(datetime.datetime.now()) + ' Start resample. Input: ' + args.input_tif)
        main(args.input_tif, args.output_tif, args.pixel_size, args.dst_crs)
        logging.info(str(datetime.datetime.now()) + ' End resample. Result:' + args.output_tif)
    except Exception as e:
        er = str(datetime.datetime.now()) + ' ' + str(e)
        logging.error(er)
        print(er)