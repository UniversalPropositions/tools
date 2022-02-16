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
- meta-conllu-srl.py

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

## Processing assumptions
### Preprocessing
- Multiple parallel corpora datasets are combined into one parallel corpora file
- Sentences with character encoding problems (\x, \u, �) are removed from source and target language dataset
- Sentences with the number of tokens lower than 5 and greater than 80 are removed
- Sentences that does not contain at least one alpha character are removed
- Multiple spaces in sentences are replaced by one space
- Duplicated sentences are removed
### Parsing
- Stanza parser is used with processors: tokenize, pos, lemma, depparse
- In case some tokens contain space character at the end of this token we automatically strip it (for token, lemma and word)
- Multi-word tokens (https://stanfordnlp.github.io/stanza/mwt.html) are removed from output CoNLL-U file, we keep only original token
### Word alignment
- Simalign library is used (https://github.com/cisnlp/simalign) with parameters: model="bert", token_type="word", matching_methods='i" (multilingual bert model, word alignments and itermax word alignments matching method)
### Postprocessing
- Sentences from both corpora that were split into multiple sentences by Stanza are removed from all the processing results, we keep only sentences that were parsed by Stanza as single sentence.
### Reverse align
- This is the script to be executed on the pipelines completed before 2022-02-16. Do not use it for all new pipelines executed after this date because word_alignemnt.py script already saves data in proper order.

## Scripts
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
Execution log is stored in ./logs/mergeparse.log file.

### wordalignment.py
Scripts executes word alignments on two parallel text files for source and target language.
Input files are read from ./data/[pipeline]/tokenized.
Output file is stored in ./data/[pipeline]/aligned/training.align file.
Execution log is stored in ./logs/wordalignment.log file.

### merge-align.py
Used only if params.save_batch is set to true. Allows to merge all the batch results from ./data/[pipeline]/align/tmp/ to a single file that contain all sentences stored in ./data/[pipeline]/align/ folder.
Execution log is stored in ./logs/mergealign.log file.

### postprocess.py
Script removes from parsed, tokenized, aligned datasets lines that were parsed by stanza into more than one sentence. It creates new files with _ at the beginning of the file name.
Execution log is stored in ./logs/postprocess.log file.

### meta-conllu-srl.py
Script converts conllu file with SRL information inside metadata['srl'] to conllu format with SRL predicates/labels on the token level. It is possible to process one file or the group of files using special character % as the pattern replacing any string.
Execution log is stored in ./logs/meta-conllu-srl.log file.
All the replacements that were performed are visible in the log file, for example:
```
2022/01/06 12:42:55 INFO Replacements:
2022/01/06 12:42:55 INFO arg0 -> A0
2022/01/06 12:42:55 INFO arg1 -> A1
2022/01/06 12:42:55 INFO argm-loc -> AM-LOC
2022/01/06 12:42:55 INFO argm-adv -> AM-ADV
2022/01/06 12:42:55 INFO argm-dis -> AM-DIS
2022/01/06 12:42:55 INFO argm-tmp -> AM-TMP
2022/01/06 12:42:55 INFO arg2 -> A2
2022/01/06 12:42:55 INFO argm-neg -> AM-NEG
```
If listed replacements are not correct it is necessary to modify fix_name function in the script.

In case SRL information is not available for a given sentence - this sentence will be just moved to the output file without any processing and information about it will be stored in the log:
```
2022/01/06 12:56:12 INFO Sentence 1 - SRL metadata not available
```
There is one constant in the script that allow to decide which field determines predicate:
```
PREDICATE_FIELD = ‘roleset’ #or ‘frameFile’
```
Sample script execution for single file:
```
python3 meta-conllu-srl.py --input_file_mask=./data/meta-conllu-srl/input/CF0001.conllu --output_file=./data/meta-conllu-srl/output/CF0001.conllu
```
Sample script execution for the group of files using name patterns:
```
python3 meta-conllu-srl.py --input_file_mask=./data/meta-conllu-srl/input/%.conllu --output_file=./data/meta-conllu-srl/output/output.conllu
```

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
python3 download.py --source=en-fr
```
### preprocess.py
```
python3 preprocess.py --pipeline=en-fr
```
### parse.py
```
python3 parse.py --pipeline=en-fr --lang=en
python3 parse.py --pipeline=en-fr --lang=fr
```
### merga-parse.py
```
python3 merge-parse.py --pipeline=en-fr 
```
### wordalignment.py
```
python3 wordalignment.py --pipeline=en-fr
```
### merge-align.py
```
python3 merge-align.py --pipeline=en-fr 
```
### postprocess.py
```
python3 postprocess.py --pipeline=en-fr 
```
### reverse-align.py
```
python3 reverse-align.py --pipeline=en-fr
```