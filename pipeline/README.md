VGG Text Search Pipeline
========================

Author:

 + Ernesto Coto, University of Oxford – <ecoto@robots.ox.ac.uk>

Usage
-----

The data-ingestion pipeline uses the same settings as the VGG Text Search Service. Therefore, please go to the `service` directory at the root of the repository and check the `settings.py` file:

 1. Make sure that `LUCENE_INDEX` points to the location of the text-index. If the directory does not exist it will be created. If it exists and you have not indexed any files before, make sure the directory is empty (this includes hidden files). If it exists and you have indexed files before, be aware that any newly ingested files will be added to the text-index.
 2. Make sure that `TEXT_RESULTS_DIR` points to the location where the text detection results are located. Note that existing files will be overwritten if an image with the same name and path is processed again.

Once you have checked the settings, make sure the text-service is not running. If it is, please shut it down before data-ingestion.

At this point, you can run the data-ingestion pipeline. Below you will find the syntax of the command for Linux/macOS. For Windows, the syntax is the same but use `start_pipeline.bat`.

    ./start_pipeline.sh input_type input_file dataset_folder

where:

 + `input_type`: should be "video" if you are running the data-ingestion with videos or "images" if you are running the data-ingestion with images. The quotes around "video" and "images" are just for clarity, do not use then when invoking the pipeline script.
 + `input_file`: should be the full path to ONE video if `input_type` is "video". Otherwise, it should be the full path to a text file containing the list of images to ingest. In this last case, the paths inside the text file should be relative to the `dataset_folder`.
 + `dataset_folder`: should be the full path to the base folder holding the images of your dataset. If you are ingesting videos, selected frames from the video will be copied to your dataset folder. If you are ingesting images, the images should be already in your `dataset_folder`.

After the data-ingestion is finished, you will need to start/restart the VGG Text Service to perform text-searches over the new data.

