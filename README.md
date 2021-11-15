# UniversalPropositions 2.0 - processing scripts

## Description
Three scripts are available:
- preprocess.py
- parsing.py
- word_alignment.py

### preprocess.py
Script prepares parallel corpus based on two datasets: europarl and tatoeba removing:
- sentences that does not contain any alpha characters
- sentences that have less than min_tokens or more than max_tokens
- duplicate sentences
Information about removed sentences is stored in log file.

### parsing.py
Script executes stanza tokenization on a given list of sentences for a given language and produces output ConLLu file.

### word_alignment.py
Scripts executes word alignments on two parallel text files for source and target language.

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

## Executing preprocessing (preprocess.py) script - example for EN-PL dataset
```
python.exe preprocess.py '--europarl_src=./data/en-pl/input/europarl/europarl-v7.pl-en.en' '--europarl_tgt=./data/en-pl/input/europarl/europarl-v7.pl-en.pl' '--tatoeba=./data/en-pl/input/tatoeba/Sentence pairs in English-Polish - 2021-11-14.tsv' '--output_src=./data/en-pl/preprocess/sentences.en' '--output_tgt=./data/en-pl/preprocess/sentences.pl' '--output_log=./data/en-pl/preprocess/log' '--min_tokens=2' '--max_tokens=50'
```
