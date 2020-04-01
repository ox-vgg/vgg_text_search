#!/bin/bash

# - This script is to be run in a clean Ubuntu 16 LTS machine, by a sudoer user.
# - The directory /webapps/ should not exist
# - Note that a python virtual environment is created on /webapps/, so you need
#   to activate the environment before running the service
# - The text recognizer installed is Yang Liu's Text-Detect-Recognize.
#   See https://github.com/lyyangduo/Text-Detect-Recognize

# update repositories
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update

# install apt-get dependencies
sudo apt-get install -y python-pip python3-pip
sudo apt-get install -y python-dev python3.6-dev
sudo apt-get install -y wget unzip cmake
sudo apt-get install -y libz-dev libjpeg-dev libfreetype6-dev
sudo apt-get install -y openjdk-8-jdk
sudo apt-get install -y ant
sudo apt-get install -y --no-install-recommends libboost-all-dev

# install virtualenv
sudo pip install configparser==4.0.2
sudo pip install virtualenv==20.0.7
pip install --upgrade pip
pip install zipp

# create main folder and virtualenv
sudo mkdir /webapps/
sudo chmod 777 /webapps/
cd /webapps/
virtualenv -p python3.6 .
source ./bin/activate

# setup folders and download git repo
wget https://gitlab.com/vgg/vgg_text_search/-/archive/master/vgg_text_search-master.zip -O /tmp/vgg_text_search.zip
unzip /tmp/vgg_text_search.zip -d /webapps/
mv /webapps/vgg_text_search*  /webapps/vgg_text_search
sed -i "s|ffmpeg|/webapps/vgg_text_search/dependencies/ffmpeg/ffmpeg|g" /webapps/vgg_text_search/pipeline/start_pipeline.sh
rm -rf /webapps/vgg_text_search/data/images.index/.gitignore

# install python dependencies
pip install Pillow==6.1.0 tensorflow==1.1.0 setproctitle==1.1.10 matplotlib==3.1.1 opencv-python==4.1.1.26 cython==0.29.14 tqdm==4.37.0
pip install https://download.pytorch.org/whl/cu90/torch-1.1.0-cp36-cp36m-linux_x86_64.whl
pip install https://download.pytorch.org/whl/cu90/torchvision-0.3.0-cp36-cp36m-manylinux1_x86_64.whl
pip install scipy==1.1.0 imgaug==0.3.0 tensorboardx==1.9 editdistance==0.5.3 simplejson==3.8.2 Flask==0.10.1

# download and install JCC and pylucene
wget https://archive.apache.org/dist/lucene/pylucene/pylucene-8.1.1-src.tar.gz -P /tmp
cd /tmp
tar -xvzf pylucene-8.1.1-src.tar.gz
cd /tmp/pylucene-8.1.1/jcc/
sed -i 's|java-8-oracle|java-8-openjdk-amd64|g' setup.py
python setup.py build
python setup.py install
cd /tmp/pylucene-8.1.1
sed -i 's|# Linux     (Debian Jessie 64-bit, Python 3.4.2|\nPREFIX_PYTHON=/webapps\nANT=JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 /usr/bin/ant\nPYTHON=$(PREFIX_PYTHON)/bin/python3\nJCC=$(PYTHON) -m jcc --shared\nNUM_FILES=10\n#|g' Makefile
make
make install

# Install Yang Liu's Text-Detect-Recognize and download static ffmpeg
wget https://github.com/ox-vgg/Text-Detect-Recognize/archive/master.zip -O /tmp/text-detect-master.zip
unzip /tmp/text-detect-master.zip -d /webapps/vgg_text_search/dependencies
mv /webapps/vgg_text_search/dependencies/Text-Detect-Recognize* /webapps/vgg_text_search/dependencies/Text-Detect-Recognize
rm -rf /webapps/vgg_text_search/dependencies/Text-Detect-Recognize/detection/pixel_link/pylib
wget https://github.com/dengdan/pylib/archive/python3.zip -O /tmp/pylib.zip
unzip /tmp/pylib.zip -d /webapps/vgg_text_search/dependencies/Text-Detect-Recognize/detection/pixel_link/
mv /webapps/vgg_text_search/dependencies/Text-Detect-Recognize/detection/pixel_link/pylib* /webapps/vgg_text_search/dependencies/Text-Detect-Recognize/detection/pixel_link/pylib
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -O /tmp/ffmpeg-release-amd64-static.tar.xz
tar -xf /tmp/ffmpeg-release-amd64-static.tar.xz -C /webapps/vgg_text_search/dependencies/
mv /webapps/vgg_text_search/dependencies/ffmpeg* /webapps/vgg_text_search/dependencies/ffmpeg

# Compile shot detector
cd /webapps/vgg_text_search/pipeline
mkdir build
cd build
cmake -DBoost_INCLUDE_DIR=/usr/include/ ../
make

# remove all zips
rm -rf /tmp/*.zip
rm -rf /tmp/*.tar*
rm -rf /tmp/pylucene-8.1.1/

# Download models from https://drive.google.com/drive/folders/1PuLCYVG457UOFzWHz4GuerTzWABZR0b6
# The contents of pixel_link_vgg_4s.zip should be unzip to:
#    /webapps/vgg_text_search/dependencies/Text-Detect-Recognize/detection/pixel_link/model
# The 0_480000.pth file should be copied to:
#    /webapps/vgg_text_search/dependencies/Text-Detect-Recognize/recognition/attention_net/model
