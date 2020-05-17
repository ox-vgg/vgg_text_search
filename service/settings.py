__author__      = 'Ernesto Coto'
__copyright__   = 'January 2020'

import os
FILE_DIR = os.path.dirname(os.path.realpath(__file__))

HOST = 'localhost'

PORT = 55366

MAX_RESULTS_RETURN = 5000

DEPENDENCIES_PATH = os.path.join(FILE_DIR, '..', 'dependencies')

# Index of the images in the dataset
LUCENE_INDEX = os.path.join(FILE_DIR, '..', 'data', 'images.index')

# Path to directory containing text detections on images
TEXT_RESULTS_DIR = os.path.join(FILE_DIR, '..', 'data', 'text_detections')

# Path to file containing word frequencies
WORD_FREQUENCY_FILE = os.path.join(FILE_DIR, '..', 'data', 'word_freq.txt')
