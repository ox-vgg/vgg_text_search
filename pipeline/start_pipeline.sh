#!/bin/bash
# Parameters:
# $1 -> Type of input: "video" or "images"
# $2 -> If input type is "video": Full path to video. If input type is "images": Full path to base folder holding the images referenced by the search service
# $3 -> If input type is "video": Full path to base folder holding the images referenced by the search service. If input type is "images": Full path to text file containing list of images to ingest
# $4 -> Full path to output features file (optional)

#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:<additional paths>
BASEDIR=$(dirname "$0")
cd "$BASEDIR"
source ../../bin/activate
if [ "$1" = "video" ]; then
    echo "Not supported yet!"
else
    echo "Not supported yet!"
fi
