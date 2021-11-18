# UniversalPropositions 2.0 - processing scripts

## Description
Three scripts are available:
- preprocess.py
- parse.py
- wordalignment.py

### preprocess.py
Script prepares parallel corpus based on two datasets: europarl and tatoeba removing:
- sentences that does not contain any alpha characters
- sentences that have less than min_tokens or more than max_tokens
- duplicated sentences
- some problematic characters from sentences
Information about removed sentences is stored in log file.

### parse.py
Script executes stanza tokenization on a given list of sentences for a given language and produces output ConLLu file and output tokenized file.

### wordalignment.py
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
## Libraries
Visit https://pytorch.org/get-started/locally/ and select appropriate version for your environment. For example for Windows pip with Cuda 11.3 it will be command as in the first line below.
Install all required libraries:
```
pip3 install torch==1.10.0+cu113 torchvision==0.11.1+cu113 torchaudio===0.10.0+cu113 -f https://download.pytorch.org/whl/cu113/torch_stable.html
pip install --upgrade git+https://github.com/cisnlp/simalign.git#egg=simalign
pip install -r requirements.txt
```
## EN-FR dataset - 200k
Below information how to execute each script. This is important to keep this order.
### Preprocess
```
python.exe preprocess.py --europarl_src=./data/source/en-fr/europarl/europarl-v7.fr-en.en --europarl_tgt=./data/source/en-fr/europarl/europarl-v7.fr-en.fr --tatoeba="./data/source/en-fr/tatoeba/Sentence pairs in English-French - 2021-11-15.tsv" --output_src=./data/en-fr-200k/bitext_raw/en-fr.en.txt --output_tgt=./data/en-fr-200k/bitext_raw/en-fr.fr.txt --output_log=./data/en-fr-200k/bitext_raw/log --min_tokens=5 --max_tokens=80 --max_sentences=200000 --split_ratio=0.2
```
### Parse
```
python.exe parse.py --input_file=./data/en-fr-200k/bitext_raw/en-fr.en.txt --output_parsed_file=./data/en-fr-200k/parsed/en-fr.en.parse.conllu --output_tokenized_file=./data/en-fr-200k/tokenized/en-fr.en.tokenized.txt --gpu=True --pool_size=4 --batch_size=10000 --cuda_devices=1 --lang=en
```
```
python.exe parse.py --input_file=./data/en-fr-200k/bitext_raw/en-fr.fr.txt --output_parsed_file=./data/en-fr-200k/parsed/en-fr.fr.parse.conllu --output_tokenized_file=./data/en-fr-200k/tokenized/en-fr.fr.tokenized.txt --gpu=True --pool_size=4 --batch_size=10000 --cuda_devices=1 --lang=fr
```
### Word alignments
```
python.exe wordalignment.py --input_tokenized_source=./data/en-fr-200k/tokenized/en-fr.en.tokenized.txt --input_tokenized_target=./data/en-fr-200k/tokenized/en-fr.fr.tokenized.txt --output_file=./data/en-fr-200k/aligned/training.align --gpu=True --pool_size=3 --batch_size=10000 --cuda_devices=1
```