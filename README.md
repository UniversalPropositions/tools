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
python.exe preprocess.py '--europarl_src=./data/source/en-pl/europarl/europarl-v7.pl-en.en' '--europarl_tgt=./data/source/en-pl/europarl/europarl-v7.pl-en.pl' '--tatoeba=./data/source/en-pl/tatoeba/Sentence pairs in English-Polish - 2021-11-14.tsv' '--output_src=./data/en-pl/bitext_raw/en-pl.en.txt' '--output_tgt=./data/en-pl/bitext_raw/en-pl.pl.txt' '--output_log=./data/en-pl/bitext_raw/log' '--min_tokens=5' '--max_tokens=80' '--max_sentences=200000' '--split_ratio=0.8'
```
## Executing preprocessing (preprocess.py) script - example for EN-FR dataset - full
```
python.exe preprocess.py '--europarl_src=./data/source/en-fr/europarl/europarl-v7.fr-en.en' '--europarl_tgt=./data/source/en-fr/europarl/europarl-v7.fr-en.fr' '--tatoeba=./data/source/en-fr/tatoeba/Sentence pairs in English-French - 2021-11-15.tsv' '--output_src=./data/en-fr/bitext_raw/en-fr.en.txt' '--output_tgt=./data/en-fr/bitext_raw/en-fr.fr.txt' '--output_log=./data/en-fr/bitext_raw/log' '--min_tokens=5' '--max_tokens=80' '--max_sentences=0' '--split_ratio=0'
```
## Executing preprocessing (preprocess.py) script - example for EN-FR dataset - 200k
```
python.exe preprocess.py '--europarl_src=./data/source/en-fr/europarl/europarl-v7.fr-en.en' '--europarl_tgt=./data/source/en-fr/europarl/europarl-v7.fr-en.fr' '--tatoeba=./data/source/en-fr/tatoeba/Sentence pairs in English-French - 2021-11-15.tsv' '--output_src=./data/en-fr-200k/bitext_raw/en-fr.en.txt' '--output_tgt=./data/en-fr-200k/bitext_raw/en-fr.fr.txt' '--output_log=./data/en-fr-200k/bitext_raw/log' '--min_tokens=5' '--max_tokens=80' '--max_sentences=200000' '--split_ratio=0.2'
```
