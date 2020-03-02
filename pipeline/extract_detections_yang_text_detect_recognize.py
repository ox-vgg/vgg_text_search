__author__      = 'Ernesto Coto'
__copyright__   = 'February 2020'

import pickle
import os
import sys
import argparse
import platform
import shutil

# add the web service folder to the sys path
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(DIR_PATH, '..', 'service'))
import settings

TEXT_RESULTS_DIR = settings.TEXT_RESULTS_DIR

if __name__ == '__main__':
    if 'Windows' in platform.system():
        freeze_support() # a requirement for windows execution

    # check arguments before continuing
    parser = argparse.ArgumentParser(description="Text recognition extractor from Yang Liu's Text-Detect-Recognize module")
    parser.add_argument('input_type', metavar='input_type', type=str, help="Type of input to the pipeline: 'images' or 'video'")
    parser.add_argument('recognition_file', metavar='recognition_file', type=str, help='Full path to Recognition.pkl file')
    parser.add_argument('dataset_base_path', metavar='dataset_base_path', type=str, help='Base path of image dataset')
    parser.add_argument('-o', dest='output_file', default='text_detections.txt', help='Full path to output file containing list of text detections files')
    args = parser.parse_args()

    # load recognitions
    with open(args.recognition_file, 'rb') as fin:
        dets = pickle.load(fin)

    if len(dets) == 0:
        print ("ERROR: No contents in detection file %s. Something went wrong !" % (args.recognition_file))
        sys.exit(1)

    # if the input was a video, then we have to identify which files
    # contain text and then copy those files to the dataset base path
    if args.input_type == 'video':
        a_path = list(dets)[0]
        video_folder = a_path.split(os.path.sep)[-2]
        video_folder = os.path.join(args.dataset_base_path, video_folder)
        if not os.path.exists(video_folder):
            os.makedirs(video_folder)
        pre_video_folder = os.path.sep.join(a_path.split(os.path.sep)[:-2]) + os.path.sep
        redirected_dets = {}
        for filepath in dets:
            # only deal with non-empty recognitions
            if len(dets[filepath]) > 0 :
                redirected_path = filepath.replace(pre_video_folder,'')
                redirected_path = os.path.join(args.dataset_base_path, redirected_path)
                redirected_dets[redirected_path] = dets[filepath]
                shutil.copyfile(filepath, redirected_path)
        dets = redirected_dets

    # For the indexing, create a file with a list of detections files
    all_text_detections = open(args.output_file,'w')

    # Now, for each file with recognitions
    for filepath in dets:

        # check that the path makes sense for us
        if not filepath.startswith(args.dataset_base_path):
            print ("ERROR: %s is not contained in %s. Skipping !" % (filepath, args.dataset_base_path))

        # only deal with non-empty recognitions
        if len(dets[filepath]) > 0:

            # create the directory for the detections file inside TEXT_RESULTS_DIR (if needed)
            relative_path = filepath.replace(args.dataset_base_path,'')
            if relative_path.startswith(os.path.sep):
                relative_path = relative_path[1:]
            relative_path_dir = os.path.dirname(relative_path)
            text_detection_dir = os.path.join(settings.TEXT_RESULTS_DIR, relative_path_dir)
            if not os.path.exists(text_detection_dir):
                os.makedirs(text_detection_dir)

            # create detections file
            text_detection_file = os.path.join(text_detection_dir, os.path.basename(filepath) + '.txt')
            print ("Creating detection file: ", text_detection_file)
            with open(text_detection_file, 'w') as fout:
                for det in dets[filepath]:
                    print ("+ detected word: ", det[0])
                    fout.write("%s\t%f\t%f\t%f\t%f\t%f\n" % (det[0], det[1], det[2], det[3], det[4]-det[2], det[5]-det[3] ))

            # save to overall list of detections files
            all_text_detections.write(text_detection_file + '\n')

    # the list of detections files is finished
    all_text_detections.close()
