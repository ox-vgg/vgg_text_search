__author__      = 'Ernesto Coto'
__copyright__   = 'January 2020'

import os
FILE_DIR = os.path.dirname(os.path.realpath(__file__))

HOST = 'localhost'

PORT = 55366

MAX_RESULTS_RETURN = 5000

# Index of the images in the dataset
LUCENE_INDEX = os.path.join(FILE_DIR, '..', 'data', 'images.index')

# Path to directory containing text detections on images
TEXT_RESULTS_DIR = os.path.join(FILE_DIR, '..', 'data', 'text_detections')
