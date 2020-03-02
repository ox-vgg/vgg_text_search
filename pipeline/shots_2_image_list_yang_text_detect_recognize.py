__author__      = 'Ernesto Coto'
__copyright__   = 'February 2020'

import os
import argparse
import platform

if __name__ == '__main__':
    if 'Windows' in platform.system():
        freeze_support() # a requirement for windows execution

    # check arguments before continuing
    parser = argparse.ArgumentParser(description="Convert list of shots to a list of filenames")
    parser.add_argument('shot_boundaries', metavar='shot_boundaries', type=str, help='Full path to a file created with our shot boundary detector')
    parser.add_argument('shot_img_base_path', metavar='shot_img_base_path', type=str, help='Base path of shot boundary images')
    parser.add_argument('-o', dest='output_file', default='file_list.txt', help='Full path to output file containing the list of files corresponding to the shot boundaries')
    args = parser.parse_args()

    # acquire shots list
    shots_list = []
    with open(args.shot_boundaries) as fshots:
        for line in fshots:
            if len(line) > 0:
                line = line.replace('\n', '')
                ashot = line.split(' ')
                for boundary in ashot:
                    if boundary not in shots_list:
                        shots_list.append(boundary)

    shots_list.sort()

    with open(args.output_file, 'w') as imglist:
        for boundary in shots_list:
            imglist.write(os.path.join(args.shot_img_base_path, boundary + '.jpg\n'))
