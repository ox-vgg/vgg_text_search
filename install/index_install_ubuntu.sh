#!/bin/bash

# - This script is to be run in a clean Ubuntu 16 LTS machine, by a sudoer user.
# - VGG_TEXT_SRC_FOLDER should not exist
# - Note that a python virtual environment is created on $VGG_TEXT_SRC_FOLDER, so you need
#   to activate the environment before running the service

VGG_TEXT_INSTALL_FOLDER="$HOME"
VGG_TEXT_SRC_FOLDER="$VGG_TEXT_INSTALL_FOLDER/vgg_text_search"

# update repositories
sudo apt-get update

# install apt-get dependencies
sudo apt-get install -y python-pip python3-pip
sudo apt-get install -y python-dev python3-dev
sudo apt-get install -y wget unzip
sudo apt-get install -y openjdk-8-jdk
sudo apt-get install -y ant

# setup folders and download git repo
cd $VGG_TEXT_INSTALL_FOLDER
wget https://gitlab.com/vgg/vgg_text_search/-/archive/master/vgg_text_search-master.zip -O /tmp/vgg_text_search.zip
unzip /tmp/vgg_text_search.zip -d $VGG_TEXT_INSTALL_FOLDER/
mv $VGG_TEXT_INSTALL_FOLDER/vgg_text_search*  $VGG_TEXT_SRC_FOLDER

# create virtual environment and install python dependencies
cd $VGG_TEXT_SRC_FOLDER
sudo pip install virtualenv
pip install --upgrade pip
pip install zipp
virtualenv -p python3 .
source ./bin/activate
pip install setuptools==40.4.3
pip install simplejson==3.8.2
pip install Flask==0.10.1

# download and install JCC and pylucene
wget https://archive.apache.org/dist/lucene/pylucene/pylucene-8.1.1-src.tar.gz -P /tmp
cd /tmp
tar -xvzf pylucene-8.1.1-src.tar.gz
cd /tmp/pylucene-8.1.1/jcc/
sed -i 's|java-8-oracle|java-8-openjdk-amd64|g' setup.py
python setup.py build
python setup.py install
cd /tmp/pylucene-8.1.1
sed -i 's|# Linux     (Debian Jessie 64-bit, Python 3.4.2|\nPREFIX_PYTHON='$VGG_TEXT_INSTALL_FOLDER'/vgg_text_search\nANT=JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64 /usr/bin/ant\nPYTHON=$(PREFIX_PYTHON)/bin/python3\nJCC=$(PYTHON) -m jcc --shared\nNUM_FILES=10\n#|g' Makefile
make
make install
cd $VGG_TEXT_INSTALL_FOLDER

# remove all zips
rm -rf /tmp/*.zip
rm -rf /tmp/*.tar*
rm -rf /tmp/pylucene-8.1.1/
