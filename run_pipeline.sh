#!/bin/bash

PIPELINE=$1

# Set - as the delimiter
IFS='-'

#Read the split words into an array based on space delimiter
read -a strarr <<< "$PIPELINE"

echo "source : ${strarr[0]}"
echo "target : ${strarr[1]}"

##Count the total words
#echo "There are ${#strarr[*]} words in the text."

## Print each value of the array by using the loop
#for val in "${strarr[@]}";
#do
#  printf "$val\n"
#done
#
python preprocess.py --pipeline="$PIPELINE"
python parse.py --pipeline="$PIPELINE" --lang="${strarr[0]}"
python parse.py --pipeline="$PIPELINE" --lang="${strarr[1]}"
python merge-parse.py --pipeline="$PIPELINE"
python wordalignment.py --pipeline="$PIPELINE"
python merge-align.py --pipeline="$PIPELINE"
