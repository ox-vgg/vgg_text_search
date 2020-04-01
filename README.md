VGG Text Search
===============

Author:

 + Ernesto Coto, University of Oxford – <ecoto@robots.ox.ac.uk>

License: BSD (see `LICENSE.md`)

Overview
--------

This repository includes a text-search service meant to serve requests generated by the [vgg_frontend](https://gitlab.com/vgg/vgg_frontend) web interface. However, it could be easily adapted to serve other clients. The source code for the service is located in the `service` folder. See the `Usage` section below.

The service is supposed to query a text-index containing words acquired from text detection results on an image dataset. That is, text files containing words and their locations within the images of the dataset. If you are annotating manually the images of a dataset with text detections or simply text labels, this tool can also help you check your annotations by searching the dataset for the words/labels you have used in your annotations and also checking all possible annotations found in the text detections results. See the README file inside `data` for more information about the format of the results to be indexed. 

The service is supposed to search for words in the text-index and then retrieve the results. For this to work, the text-index must be built before hand. The scripts to perform this task are located inside the `utils` folder. See the README file inside `utils` for more information.

***Full-system***: If you do not have a set of text detection results, you can generate one from a set of images or a video file. The full-system includes `ffmpeg` and [Yang Liu's Text-Detect-Recognize](https://github.com/lyyangduo/Text-Detect-Recognize) software, which is be able to detect and recognize text from an image. The scripts in the `pipeline` folder will allow you to process an image folder or a video with that software, and automatically index the results for later retrieval with the text-search service.

Supported platforms
-------------------

Successfully deployed on Ubuntu 16 LTS. See the README inside the `install` folder to find an example installation script.

Usage
-----

The text-index must be built before running the service. See the README file inside `utils` for information on building the index.

For the ***Full-system***, use the scripts in the `pipeline` folder to process an image folder or a video, and build the index automatically.

After the index has been built, check the `service/settings.py` file and change the location of the text-index and the text-detections if needed. Then, just go to the `service` folder and execute:

	python backend.py

The service will start running by default in port 55366. You can also change this port number and other settings by editing the `service/settings.py` file.

Dependencies
------------

The VGG Text Search heavily depends on:

 + Java: Tested with OpenJDK 8 under Ubuntu 16 LTS.
 + Python [JCC v3.6](https://pypi.python.org/pypi/JCC/3.6)
 + [PyLucene](http://lucene.apache.org/pylucene/) v8.1.1. Download the source from <https://archive.apache.org/dist/lucene/pylucene/pylucene-8.1.1-src.tar.gz> and compile it.
 + [Flask](http://flask.pocoo.org/) (tested with v0.10.1).
 + simplejson

For the ***Full-system***, see the additional dependencies in [Yang Liu's Text-Detect-Recognize](https://github.com/lyyangduo/Text-Detect-Recognize) github page.

ACKs
----

This software has been derived from the work of Max Jaderberg <http://www.robots.ox.ac.uk/~vgg/research/text/index.html>

