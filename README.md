# UniversalPropositions 2.0 - tools

## Virtual Environment
```
mkdir envs
cd envs
python3 -m venv up
cd ..
source envs/up/bin/activate
pip install --upgrade pip
```
## Libraries
Visit https://pytorch.org/get-started/locally/ and select appropriate version for your environment. For example for Windows pip with Cuda 11.3:
```
pip3 install torch==1.10.0+cu113 torchvision==0.11.1+cu113 torchaudio===0.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
```
For Mac OS X:
```
pip3 install torch
```
Other libraries:
```
pip install --upgrade git+https://github.com/cisnlp/simalign.git#egg=simalign
pip install -r requirements.txt
```
## Description
Repository contains two groups of scripts. 
Scripts to be executed before bootstrap training:
- download.py
- preprocess.py
- parse.py
- merge_parse.py
- wordalignment.py
- merge_align.py
- postprocess.py
Script to be executed after bootstrap training:
- spade_to_up.py
- merge_ud_up.py

## Configuration file
Configuration file location is: config/config.json.
Configuration file attributes:
- params
    - min_tokens - minimal number of tokens in sentences
    - max_tokens - maximal number of tokens in sentences
    - gpu (true/false) - processing on gpu or cpu
    - processes - number of parallel processes to be started
    - batch_size - number of sentences processed in one batch
    - batch_save - (true/false) results saved to the file after each batch and not saved at the end of the processing, in case true is set it is required to run merge_parse.py or merge_align.py respectively after parse.py and wordalignment.py processing to get one file with all sentences
    - limit - the number of sentences to be processed, 0 - means all sentences will be processed
- pipelines (key-value) - key is the pipeline name used as argument for all processing scripts except download.py
    - source - reference to sources and datasets to be processed
    - sentences
        - europarl (optional) - number of sentences to be selected from europarl dataset, 0 - means all
        - tatoeba (optional) - number of sentences to be selected from tatoeba dataset, 0 - means all
        - subtitles (optional) -  - number of sentences to be selected from subtitles dataset, 0 - means all
- sources (key-value) - key is the name used as argument for download.py processing
    - src_lang - parallel corpus source language - always en
    - tgt_lang - parallel corpus target language
    - datasets
        - europarl (optional) - url to europarl dataset
        - tatoeba (optional) - url to tatoeba dataset
        - subtitles (optional) - url to subtitles dataset

## Processing assumptions
### Preprocessing
- Multiple parallel corpora datasets are combined into one parallel corpora file
- Sentences with character encoding problems (\x, \u, �) are removed from source and target language dataset
- Sentences with the number of tokens lower than 5 and greater than 80 are removed
- Sentences that does not contain at least one alpha character are removed
- Multiple spaces in sentences are replaced by one space
- Duplicate sentences are removed
### Parsing
- Stanza parser is used with processors: tokenize, pos, lemma, depparse
- In case some tokens contain space character at the end of this token we automatically strip it (for token, lemma and word)
- Multi-word tokens (https://stanfordnlp.github.io/stanza/mwt.html) are removed from output CoNLL-U file, we keep only original token
### Word alignment
- Simalign library is used (https://github.com/cisnlp/simalign) with parameters: model="bert", token_type="word", matching_methods='i" (multilingual bert model, word alignments and itermax word alignments matching method)
### Postprocessing
- Sentences from both corpora that were split into multiple sentences by Stanza are removed from all the processing results, we keep only sentences that were parsed by Stanza as single sentence.

## Scripts description
### download.py
Script downloads selected parallel corpus based on configuration defined in config/config.json file.

### preprocess.py
Script prepares parallel corpus based on datasets in moses format configured in config/config.json file.

Processing results are stored in ./data/[pipeline]/bitext_raw/ folder.
Information about removed sentences is stored in the same folder in the preprocess.log file.
It is possible to limit the number of sentences in the pipeline configuration.
Execution log is stored in ./logs/preprocess.log file.

### parse.py
Script executes stanza tokenization on a given list of sentences for a given language and produces output CoNLL-U file and output tokenized file.
Input files are read from ./data/[pipeline]/bitext_raw/ folder.
Output files are stored in: ./data/[pipeline]/parsed/ and ./data/[pipeline]/tokenized/ folders.
Execution log is stored in ./logs/parse.log file.

### merge-parse.py
Used only if params.save_batch is set to true. Allows to merge all the batch results from ./data/[pipeline]/tokenized/tmp/ and ./data/[pipeline]/parsed/tmp to single files that contain all sentences stored in ./data/[pipeline]/tokenized/ and ./data/[pipeline]/parsed/ folders.
Execution log is stored in ./logs/merge_parse.log file.

### wordalignment.py
Scripts executes word alignments on two parallel text files for source and target language.
Input files are read from ./data/[pipeline]/tokenized.
Output file is stored in ./data/[pipeline]/aligned/training.align file.
Execution log is stored in ./logs/wordalignment.log file.

### merge-align.py
Used only if params.save_batch is set to true. Allows to merge all the batch results from ./data/[pipeline]/align/tmp/ to a single file that contains all sentences stored in ./data/[pipeline]/align/ folder.
Execution log is stored in ./logs/merge-align.log file.

### postprocess.py
Script removes from parsed, tokenized, aligned datasets lines that were parsed by stanza into more than one sentence. It creates new files with _ at the beginning of the file name.
Execution log is stored in ./logs/postprocess.log file.

### spade_to_up.py
Script creates a new conllu file based on UD conllu file and spade conllu file.

### merge_ud_up.py
Script merges UD and UP files.

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
python3 up2/download.py --source=en-fr
```
### preprocess.py
```
python3 up2/preprocess.py --pipeline=en-fr
```
### parse.py
```
python3 up2/parse.py --pipeline=en-fr --lang=en
python3 up2/parse.py --pipeline=en-fr --lang=fr
```
### merge_parse.py
```
python3 up2/merge_parse.py --pipeline=en-fr 
```
### wordalignment.py
```
python3 up2/wordalignment.py --pipeline=en-fr
```
### merge_align.py
```
python3 up2/merge_align.py --pipeline=en-fr 
```
### postprocess.py
```
python3 up2/postprocess.py --pipeline=en-fr 
```
### spade_to_up.py
```
python3 up2/spade_to_up.py --source=UD_Hindi-HDTB/hi_hdtb-ud-dev.conllu --input_ud=./data/ud/hi/hi_hdtb-ud-dev.conllu --input_spade=./data/ud/hi/hi_hdtb-ud-dev.conllu.spade.conllu --output=./data/ud/hi/hi_hdtb-up-dev.conllu
```
### merge_ud_up.py
```
python3 up2/merge_ud_up.py --input_ud=./data/ud/hi/hi_hdtb-ud-dev.conllu --in
put_up=./data/ud/hi/hi_hdtb-up-dev.conllu --output=./data/ud/hi/hi_hdtb-srl-dev.conllu
```