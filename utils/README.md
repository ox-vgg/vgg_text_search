VGG Text Search - Utils
=======================

Author:

 + Ernesto Coto, University of Oxford - <ecoto@robots.ox.ac.uk>

Overview
--------

The scripts in this folder can be used to build/explore the image index:

 + `index_results.py`: Application used to build the index for the text detections in the dataset of images. Before using this application you need to generate the results files containing the text detections for each image in the dataset. The format of these files is explained in the README at the `data` folder of the repository. The following example creates the index in the `images.index` directory, out of a list of result files in `/results/fnlist.txt`, with each results file stored under `/results/`:

		python index_results.py /results/fnlist.txt /results/ images.index

 + `word_cloud.py`: Application used to generate a text file with a list of the most frequent words in the `images.index`. This can be used later in the frontend as input for a wordcloud. The following example creates the `word_freq.txt` file, out of a list of result files in `/results/fnlist.txt`, with each results file stored under `/results/`:

		python word_cloud.py /results/fnlist.txt /results/ word_freq.txt

 + `search_index.py`: Simple console application to perform a search in the `images.index`. In order to start the application for searching over the index in the folder `images.index`, just use:

		python search_index.py images.index

