#!/bin/bash

PIPELINE=$1

# Set - as the delimiter
IFS='-'

read -a strarr <<< "$PIPELINE"

echo "source : ${strarr[0]}"
echo "target : ${strarr[1]}"

#python scripts-py/download.py --source="${strarr[0]}-${strarr[1]}"
#python scripts-py/preprocess.py --pipeline="$PIPELINE"
#python scripts-py/parse.py --pipeline="$PIPELINE" --lang="${strarr[0]}"
#python scripts-py/parse.py --pipeline="$PIPELINE" --lang="${strarr[1]}"
#python merge-parse.py --pipeline="$PIPELINE"
#python scripts-py/wordalignment.py --pipeline="$PIPELINE"
#python merge-align.py --pipeline="$PIPELINE"
python scripts-py/postprocess.py --pipeline="$PIPELINE"
