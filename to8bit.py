import rasterio
import argparse
import numpy as np

# Normalization parameter; change to 2 to make output more contrast
WIDTH = 3


def main(ms_file, out_file, r=1, g=2, b=3):
    print("Running image preprocessing script")
    with rasterio.open(ms_file) as src:
        profile = src.profile
        red = src.read(r)
        grn = src.read(g)
        blu = src.read(b)

    profile.update(count=3, dtype='uint8')

    channels_8bit = []
    for channel in [red, grn, blu]:
        mean, std, min_val, max_val = np.mean(channel), np.std(channel), np.min(channel), np.max(channel)
        m = max(min_val, mean - WIDTH*std)
        M = min(max_val, mean + WIDTH*std)
        ch_8bit = np.floor_divide(
            np.multiply((channel - m), 255, dtype='float32'),
            (M-m)
        )
        ch_8bit = np.clip(np.around(ch_8bit, 0), 0, 255).astype('uint8')
        channels_8bit.append(ch_8bit)

    with rasterio.open(out_file, 'w', **profile) as dst:
        dst.write(channels_8bit[0], 1)
        dst.write(channels_8bit[1], 2)
        dst.write(channels_8bit[2], 3)
    print('Done')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract 8-bit RGB from the 16-bit multispectral.')
    parser.add_argument('input', type=str,
                        help='input multispectral file')
    parser.add_argument('output', type=str,
                        help='output rgb file')
    parser.add_argument('--channels', metavar='N', type=int, nargs=3,
                        help='R,G,B channels position in file', default=[1, 2, 3])

    args = parser.parse_args()
    main(args.input, args.output, r=args.channels[0], g=args.channels[1], b=args.channels[2])