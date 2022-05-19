from osgeo import gdal
import argparse

def main(input_tif, output_tif, pixel_size):

    gdal.Warp(output_tif, input_tif, xRes=pixel_size, yRes=pixel_size)
    print('End')

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('input_tif', type=str, help='input .tif file')
    parser.add_argument('output_tif', type=str, help='output .tif file')
    parser.add_argument('pixel_size', type=float, help='pixel size in metr', default=0.8)
    args = parser.parse_args()
    main(args.input_tif, args.output_tif, args.pixel_size)
