# Universal Propositions - other scripts

## spade_to_up.py
Script converts ConLL-U file with SRL annotations defined in multiple frame columns to new ConLL-U Plus format with SRL annotations in PRED, ARGHEADS columns.
```
python3 up2/other/srl_to_up.py --input=./data/gold/vi/vi_tatoeba-gold.conllu --output=./data/gold/vi/vi_tatoeba-gold-out.conllu 
```