from osgeo import gdal, osr
import argparse
import numpy
import array
import os

def main(input_tif, output_tif, pixel_size, epsg):
    print(pixel_size)

    # если проекция не указана пользователем, то используем поумолчанию 3857 и рассчитываем размер
    # пикселя в "реальных метрах"
    if epsg == 'noprj':
        epsg = '3857'

        dataset = gdal.Open(input_tif)
        print("Raster size", dataset.RasterXSize, "x", dataset.RasterYSize)
        print("Number of bands", dataset.RasterCount)
        print("Geo transform", dataset.GetGeoTransform())
        #get center rastr
        xmin, ymin, xmax, ymax = GetExtent(dataset)
        center = [(xmin + xmax) / 2, (ymin + ymax) / 2]

        # trasform cernter rastr to EPSG:4326
        proj = osr.SpatialReference(wkt=dataset.GetProjection())
        epsgid = int(proj.GetAttrValue('AUTHORITY',1))

        #input SpatialReference
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(epsgid)

        # output SpatialReference
        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(4326)

        re_center = ReprojectCoords(center, src_srs=inSpatialRef, tgt_srs=outSpatialRef)
        #print(re_center)

        TransformOnePixel(dataset, output_tif)


    warp = gdal.Warp(output_tif, input_tif, xRes=pixel_size, yRes=pixel_size, dstSRS='EPSG:' + epsg)
    warp = None
    print('End resample. Result:', output_tif)

def GetExtent(ds):

    xmin, xpixel, _, ymax, _, ypixel = ds.GetGeoTransform()
    width, height = ds.RasterXSize, ds.RasterYSize
    xmax = xmin + width * xpixel
    ymin = ymax + height * ypixel

    return xmin, ymin, xmax, ymax

def ReprojectCoords(coords,src_srs,tgt_srs):

    transform = osr.CoordinateTransformation( src_srs, tgt_srs)
    x, y, z = transform.TransformPoint(coords[0],coords[1])
    return x, y

def TransformOnePixel(dataset, output_tif):
    "создаем растр из одного пикселя с праметрами пикселя основного растра"

    #print("Raster size x:", dataset.RasterXSize, "y:", dataset.RasterYSize)

    xcenter_poi = dataset.RasterXSize // 2
    ycenter_poi = dataset.RasterYSize // 2
    print('centr_point', xcenter_poi, ycenter_poi)
    x, xsize, xrot, y, yrot, ysize = dataset.GetGeoTransform()

    xpix = (xcenter_poi * xsize) + x
    ypix = (ycenter_poi * ysize) + y

    print(xpix, ypix)

    # gdalBand = dataset.GetRasterBand(1)
    # ar = array.array('f', [1.])#gdalBand.ReadAsArray().astype(numpy.float32)
    #print(gdalBand.ReadAsArray())
    #print(array.typecodes())

    # print("Number of bands", dataset.RasterCount)
    # print("Geo transform", dataset.GetGeoTransform())

    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    # размеры растра
    cols = 1
    rows = 1
    # количество каналов
    bands = 3
    # тип данных
    dt = gdal.GDT_Byte #GDT_Float32

    pixtif = os.path.dirname(output_tif) + "/1pix.tif"
    output_pixtif =os.path.dirname(output_tif) + "/1pix_proj.tif"

    # создаем растр
    outData = driver.Create(pixtif, cols, rows, bands, dt)
    #После того, как растр создан можно добавить информацию о проекции и привязке.
    proj = dataset.GetProjection()
    outData.SetProjection(proj)
    outData.SetGeoTransform((xpix, xsize, xrot, ypix, yrot, ysize))
    # outData.GetRasterBand(1).WriteArray(ar)
    # перепроицирование пикселя
    warp = gdal.Warp(output_pixtif, pixtif, xRes=xsize, yRes=ysize, dstSRS='EPSG:3857')
    warp = None




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('input_tif', type=str, help='input .tif file')
    parser.add_argument('output_tif', type=str, help='output .tif file')
    parser.add_argument('--pixel_size', type=float, help='pixel size in meter', default=0.8)
    parser.add_argument('--epsg', type=str, help='EPSG', default='noprj')
    args = parser.parse_args()
    #print(args)
    main(args.input_tif, args.output_tif, args.pixel_size, args.epsg)