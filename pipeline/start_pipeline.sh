#!/bin/bash
# Parameters:
# $1 -> Type of input: "video" or "images"
# $2 -> If input type is "video": Full path to video. If input type is "images": Full path to base folder holding the images referenced by the search service
# $3 -> If input type is "video": Full path to base folder holding the images referenced by the search service. If input type is "images": Full path to text file containing list of images to ingest
# $4 -> Full path to output features file (optional)

#export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:<additional paths>
BASEDIR=$(dirname "$0")
cd "$BASEDIR"
PIPELINE_DIR=${PWD}
source ../../bin/activate
if [ "$1" = "video" ]; then
    echo "Not supported yet!"
else
    DATE=`date '+%d-%m-%Y %H:%M:%S'`
    echo "[$DATE]: ------- Cleaning up"
    rm -rf /tmp/text_detect_recognize
    mkdir -p /tmp/text_detect_recognize
    sed 's|^|'"${2}"'|g' "${3}" > /tmp/text_detect_recognize/file_list.txt

    DATE=`date '+%d-%m-%Y %H:%M:%S'`
    echo "[$DATE]: ------- Running detector"
    cd "${PIPELINE_DIR}/../dependencies/Text-Detect-Recognize/detection/pixel_link/"
    ./scripts/test_any.sh 0 ./model/conv3_3/model.ckpt-38055 /tmp/text_detect_recognize/file_list.txt /tmp/text_detect_recognize

    DATE=`date '+%d-%m-%Y %H:%M:%S'`
    echo "[$DATE]: ------- Running recognition"
    cd "${PIPELINE_DIR}/../dependencies/Text-Detect-Recognize/recognition/attention_net/"
    python Recognition_yang.py --detection_path /tmp/text_detect_recognize/Detection.pkl --gpus 0 --checkpoint ../attention_net/model/0_480000.pth --output_path /tmp/text_detect_recognize

    DATE=`date '+%d-%m-%Y %H:%M:%S'`
    echo "[$DATE]: ------- Extracting detections"
    cd "${PIPELINE_DIR}"
    python extract_detections_yang_text_detect_recognize.py /tmp/text_detect_recognize/Recognition.pkl "${2}" -o /tmp/text_detect_recognize/detections.txt

    DATE=`date '+%d-%m-%Y %H:%M:%S'`
    echo "[$DATE]: ------- Indexing detections"
    cd "${PIPELINE_DIR}/../service/"
    LUCENE_INDEX=$(python -c "import settings; print(settings.LUCENE_INDEX)")
    TEXT_RESULTS_DIR=$(python -c "import settings; print(settings.TEXT_RESULTS_DIR)")
    cd "${PIPELINE_DIR}/../utils/"
    echo "a" | python index_results.py /tmp/text_detect_recognize/detections.txt "${TEXT_RESULTS_DIR}" "${LUCENE_INDEX}"

    # clean up again
    rm -rf /tmp/text_detect_recognize
fi
