from osgeo import gdal, osr
import argparse

import math
import os

def main(input_tif, output_tif, pixel_size, epsg):

    # если проекция не указана пользователем, то используем поумолчанию 3857 и рассчитываем размер
    # пикселя в "реальных метрах"
    if epsg == None:
        epsg = '3857'
        dataset = gdal.Open(input_tif)

        #get center rastr
        xmin, ymin, xmax, ymax = GetExtent(dataset)
        center = [(xmin + xmax) / 2, (ymin + ymax) / 2]

        # input SpatialReference
        proj = osr.SpatialReference(wkt=dataset.GetProjection())
        epsgid = int(proj.GetAttrValue('AUTHORITY',1))
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(epsgid)

        # output SpatialReference
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(4326)
        # trasform  rastr cernter to EPSG:4326
        re_center = ReprojectCoords(center, src_srs=inSpatialRef, tgt_srs=outSpatialRef)
        # Get coefficient of real meter
        coef = math.cos(math.radians(re_center[0]))
        print(coef)
        # change pixel size
        pixel_size = pixel_size * coef


    gdal.Warp(output_tif, input_tif, xRes=pixel_size, yRes=pixel_size, dstSRS='EPSG:' + epsg)
    print('End resample. Result:', output_tif)

def GetExtent(ds):
    "Get extent of dataset raster"
    xmin, xpixel, _, ymax, _, ypixel = ds.GetGeoTransform()
    width, height = ds.RasterXSize, ds.RasterYSize
    xmax = xmin + width * xpixel
    ymin = ymax + height * ypixel
    return xmin, ymin, xmax, ymax

def ReprojectCoords(coords,src_srs,tgt_srs):
    "Reprojection coordinates"
    transform = osr.CoordinateTransformation(src_srs, tgt_srs)
    x, y, z = transform.TransformPoint(coords[0], coords[1])
    return x, y

def TransformOnePixel(dataset, output_tif):
    "!!!Это теперь не нужно, но пусть пока тут полежит вруг чё"

    "создаем растр из одного пикселя с праметрами пикселя основного растра"

    #print("Raster size x:", dataset.RasterXSize, "y:", dataset.RasterYSize)
    xcenter_poi = dataset.RasterXSize // 2
    ycenter_poi = dataset.RasterYSize // 2

    pixtif = os.path.dirname(output_tif) + "/1pix.tif"
    output_pixtif =os.path.dirname(output_tif) + "/1pix_proj.tif"

    # вырезаем один пиксель из исходного растра
    raster_1pix = gdal.Translate(pixtif, dataset, srcWin=[xcenter_poi, ycenter_poi, 1, 1])
    raster_1pix = None
    # перепроицирование пикселя
    warp = gdal.Warp(output_pixtif, pixtif, dstSRS='EPSG:3857')
    warp = None

    ds = gdal.Open(output_pixtif)
    x, xsize, xrot, y, yrot, ysize = ds.GetGeoTransform()
    return xsize, ysize


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('input_tif', type=str, help='input .tif file')
    parser.add_argument('output_tif', type=str, help='output .tif file')
    parser.add_argument('--pixel_size', type=float, help='pixel size in meter', default=0.8)
    parser.add_argument('--epsg', type=str, help='EPSG', default=None)
    args = parser.parse_args()
    main(args.input_tif, args.output_tif, args.pixel_size, args.epsg)