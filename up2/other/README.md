# Universal Propositions - other scripts

## spade_to_up.py
Script converts CoNLL-U file with SRL annotations defined in multiple frame columns to new ConLL-U Plus format with SRL annotations in PRED, ARGHEADS columns.
```
python3 up2/other/srl_to_up.py --input=./data/gold/vi/vi_tatoeba-gold.conllu --output=./data/gold/vi/vi_tatoeba-gold-out.conllu 
```
## convert_srl_format.py
Script converts CoNLL-U Plus file with SRL annotations defined as UP_PRED, UP_HEADSPAN, UP_ARGSPAN to CoNLL-U format with SRL annotations with variable number of frames.
It is important to have up to date conllup library installed on virtual environment:
```
pip install --force dist/conllup-0.1.0-py3-none-any.whl
```
It is possible to provide folders as arguments or single files.
```
python3 up2/other/convert_srl_format.py --input_up=./data/up_data --output=./data/up_data_old_format
```