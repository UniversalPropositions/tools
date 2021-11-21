# UniversalPropositions 2.0 - processing scripts

## Description
Available scripts:
- download.py
- preprocess.py
- parse.py
- wordalignment.py

### download.py
Script downloads selected parallel corpus.

### preprocess.py
Script prepares parallel corpus based on datasets in moses format configured in config/config.json file, removing:
- sentences that do not contain any alpha characters
- sentences that have tokens less than min_tokens or more than max_tokens
- duplicated sentences
- some problematic characters from sentences

Processing results are stored in ./data/[pipeline]/bitext_raw/ folder.
Information about removed sentences is stored in the same folder in the preprocess.log file.

### parse.py
Script executes stanza tokenization on a given list of sentences for a given language and produces output ConLLu file and output tokenized file.
Input files are read from ./data/[pipeline]/bitext_raw/ folder.
Output files are stored in: ./data/[pipeline]/parsed/ and ./data/[pipeline]/tokenized/ folders.

### wordalignment.py
Scripts executes word alignments on two parallel text files for source and target language.
Input files are read from ./data/[pipeline]/tokenized.
Output file is stored in ./data/[pipeline]/aligned/training.align file.

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
## Configuration
./config/config.json contains configuration file for all applications. It consists of three sections:
- params - defines processing parameters common for all applications
- pipelines - defined execution pipelines to be executed
- sources - defines datasets to be downloaded

## EN-FR dataset
This is important to keep the order of scripts execution.
### Download
```
python.exe download.py --pipeline=en-fr
```
### Preprocess
```
python.exe preprocess.py --pipeline=en-fr
```
### Parse
```
python.exe parse.py --pipeline=en-fr --lang=en
python.exe parse.py --pipeline=en-fr --lang=fr
```
### Word alignments
```
python.exe wordalignment.py --pipeline=en-fr
```