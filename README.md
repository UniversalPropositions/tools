# UniversalPropositions 2.0 - processing scripts

## Description
Available scripts:
- download.py
- preprocess.py
- parse.py
- merge-parse.py
- wordalignment.py
- merge-align.py
- postprocess.py

## Configuration file
Configuration file location is: config/config.json.
Configuration file attributes:
- params
    - min_tokens - minimal number of tokens in sentences
    - max_tokens - maximal number of tokens in sentences
    - gpu (true/false) - processing on gpu or cpu
    - processes - number of parallel processes to be started
    - batch_size - number of sentences processed in one batch
    - batch_save - (true/false) results saved to the file after each batch and not saved at the end of the processing, in case true is set it is required to run merge_parse.py or merge_align.py after processing to get one file with all sentences
    - limit - the number of sentences to be processed, 0 - means all sentences will be processed
- pipelines (map) - key is the pipeline name used as argument for all processing scripts except download.py
    - source - reference to sources and datasets to be processed
    - sentences
        - europarl (optional) - number of sentences to be selected from europarl dataset, 0 - means all
        - tatoeba (optional) - number of sentences to be selected from tatoeba dataset, 0 - means all
        - subtitles (optional) -  - number of sentences to be selected from subtitles dataset, 0 - means all
- sources (map) - key is the name used as argument for download.py processing
    - src_lang - parallel corpus source language - always en
    - tgt_lang - parallel corpus target language
    - datasets
        - europarl (optional) - url to europarl dataset
        - tatoeba (optional) - url to tatoeba dataset
        - subtitles (optional) - url to subtitles dataset

### download.py
Script downloads selected parallel corpus based on configuration defined in config/config.json file.

### preprocess.py
Script prepares parallel corpus based on datasets in moses format configured in config/config.json file, removing:
- sentences that do not contain any alpha characters
- sentences that have tokens less than min_tokens or more than max_tokens
- duplicated sentences
- some problematic characters from sentences

Processing results are stored in ./data/[pipeline]/bitext_raw/ folder.
Information about removed sentences is stored in the same folder in the preprocess.log file.
It is possible to limit the number of sentences in the pipeline configuration.

### parse.py
Script executes stanza tokenization on a given list of sentences for a given language and produces output ConLLu file and output tokenized file.
Input files are read from ./data/[pipeline]/bitext_raw/ folder.
Output files are stored in: ./data/[pipeline]/parsed/ and ./data/[pipeline]/tokenized/ folders.

### merge-parse.py
Used only if params.save_batch is set to true. Allows to merge all the batch results from ./data/[pipeline]/tokenized/tmp/ and ./data/[pipeline]/parsed/tmp to single files that contain all sentences stored in ./data/[pipeline]/tokenized/ and ./data/[pipeline]/parsed/ folders.

### wordalignment.py
Scripts executes word alignments on two parallel text files for source and target language.
Input files are read from ./data/[pipeline]/tokenized.
Output file is stored in ./data/[pipeline]/aligned/training.align file.

### merge-align.py
Used only if params.save_batch is set to true. Allows to merge all the batch results from ./data/[pipeline]/align/tmp/ to a single file that contain all sentences stored in ./data/[pipeline]/align/ folder.

### postprocess.py
Script removes from parsed, tokenized, aligned datasets lines that were parsed by stanza into more than one sentence. It creates new files with _ at the beginning of the file name.

## Python virtual environment
Create python virtual environment:
```
mkdir envs
cd envs
python3 -m venv ud20
cd ..
```
Activate python virtual environment:
```
source envs/ud20/bin/activate
```
## Libraries
Visit https://pytorch.org/get-started/locally/ and select appropriate version for your environment. For example for Windows pip with Cuda 11.3:
```
pip3 install torch==1.10.0+cu113 torchvision==0.11.1+cu113 torchaudio===0.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
```
For mac:
```
pip3 install torch torchvision torchaudio
```
Other libraries:
```
pip install --upgrade git+https://github.com/cisnlp/simalign.git#egg=simalign
pip install -r requirements.txt
```
## Folders structure
Sample folder structure
```
data
    en-fr-200k
        aligned
        bitext_raw
        parsed
        tokenized
    en-fr
        aligned
        bitext_raw
        parsed
        tokenized
    source
        en-fr
            europarl
                ...
            tatoeba
                ...
```

## Sample pipeline execution
This is important to keep the order of scripts execution.
### download.py
```
python.exe download.py --pipeline=en-fr
```
### preprocess.py
```
python.exe preprocess.py --pipeline=en-fr
```
### parse.py
```
python.exe parse.py --pipeline=en-fr --lang=en
python.exe parse.py --pipeline=en-fr --lang=fr
```
### merga-parse.py
```
python.exe merge-parse.py --pipeline=en-fr 
```
### wordalignment.py
```
python.exe wordalignment.py --pipeline=en-fr
```
### merga-align.py
```
python.exe merge-align.py --pipeline=en-fr 
```
### postprocess.py
```
python.exe postprocess.py --pipeline=en-fr 
```