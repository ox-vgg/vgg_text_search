VGG Text Search - Data
=======================

Author:

 + Ernesto Coto, University of Oxford - <ecoto@robots.ox.ac.uk>

Overview
--------

The following folders are required for the service to work:

 - `images.index`: Index of the images in the dataset. This the text-index built by the `index_results.py` script under the `utils` folder.
 - `text_detections`: Folder with text files containing the scores and bounding-boxes of the text detections for each image within the dataset. Let `<IMAGES FOLDER>` be the full path to your image dataset. For each processed image `foo.jpg` in your dataset, there should be a corresponding text file `foo.jpg.txt` inside `text_detections`, even if it is empty (when nothing was detected). Each of the text files with the detections, should be stored in a folder with the same path structure as the processed image. That means that for the image at `<IMAGES FOLDER>/<subfolder1>/<subfolder2>/foo.jpg`, the corresponding text file should be stored in a folder structure like `text_detections/<subfolder1>/<subfolder2>/foo.jpg.txt`. Each file should contain the information of one detection per line. For each detection, the line should contain: the word that was detected, it's detection score, and the detection bounding box: [ top-left-corner-x, top-left-corner-y, width, height].

