'''
Script converts conllu file with SRL information inside metadata['srl'] 
to conllu format with SRL predicates/labels on the token level
'''
import argparse
from conllu import TokenTree, parse_incr
import time
import logging
import os
import json
import glob

PREDICATE_FIELD = 'roleset'  # or 'frameFile'

replacements = {}

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/meta-conllu-srl.log"),
        logging.StreamHandler()
    ]
)


def fix_name(name: str) -> str:
    '''
    Replaces argument identifiers

    :param name: argument name
    :return: fixed argument name
    '''
    key = name
    name = name.upper()
    name = name.replace('ARGM', 'AM')
    name = name.replace('ARG', 'A')
    if key not in replacements:
        replacements[key] = name
    return name


def filter_frames_nopb(counter: int, srl: list[dict]) -> list[dict]:
    '''
    Filtering nopb rolesets

    :param counter: sentence number
    :param srl: the list of frames
    :return: filteres list of frames
    '''
    nsrl = [d for d in srl if d['roleset'] != 'nopb']
    if len(nsrl) != len(srl):
        logging.info(f'Sentence {counter} - filtered because of nopb roleset')
    return nsrl


def fix(counter: int, tokentree: TokenTree) -> TokenTree:
    '''
    Fixing selected TokenTree

    :param counter: sentence number
    :param tokentree: token tree to be fixed
    :return: fixed token tree
    '''
    if 'srl' in tokentree.metadata:
        srl_json = tokentree.metadata['srl']
        srl = json.loads(srl_json)
        # sort frames by predicate token number
        srl = sorted(srl, key=lambda item: item['target'][0])
        srl = filter_frames_nopb(counter, srl)
        for i, t in enumerate(tokentree):
            # delete multiword tokens
            if type(t['id']) == tuple:
                del tokentree[i]
            # clear deps
            tokentree[i]['deps'] = "_"
            # clear action
            tokentree[i]['action'] = "_"
            # init frames
            for j in range(0, len(srl)):
                tokentree[i]['a' + str(j+1)] = "_"

        for i, item in enumerate(srl):
            token = item['target'][0] - 1
            value = item[PREDICATE_FIELD]
            tokentree[token]['deps'] = "Y"
            tokentree[token]['action'] = value
            for arg in item['args']:
                name = arg[0]
                tokens = arg[1]
                for t in tokens:
                    tokentree[t-1]['a'+str(i + 1)] = fix_name(name)
        logging.info(f'Sentence {counter} - Processed')
        return tokentree
    else:
        logging.info(f'Sentence {counter} - SRL metadata not available')
        return None


def process_file(f: str, fulltokenlist: list[TokenTree]):
    '''
    Fixing all token trees in a given input file

    :param f: file name to be fixed
    :param fulltokenlist: the list of all token trees from a given file
    :return: fixed token tree
    '''
    with open(f, "r", encoding="utf-8") as data_file:
        counter = 0
        for tokentree_in in parse_incr(data_file, fields=fields):
            counter += 1
            tokentree_out = fix(counter, tokentree_in)
            if tokentree_out:
                fulltokenlist.append(tokentree_out)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Metadata srl to conllu token srl conversion')
    parser.add_argument('--input_file_mask', type=str)
    parser.add_argument('--output_file', type=str)

    args = parser.parse_args()

    # CONLLU format defintions
    fields = ["id", "form", "lemma", "upos", "xpos", "feads", "head", "deprel", "deps",
              "action", "a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8", "a9", "a10", "a11", "a12"]

    t0 = time.time()

    files = glob.glob(args.input_file_mask.replace("%", "*"))

    files.sort()

    folder = os.path.dirname(args.output_file)

    os.makedirs(folder, exist_ok=True)

    fulltokenlist = []

    for f in files:
        logging.info(f'Processing file: {f}')
        process_file(f, fulltokenlist)

    logging.info(f'Total number of sentences: {len(fulltokenlist)}')

    with open(args.output_file, 'w', encoding='utf8') as f:
        f.writelines([tokentree.serialize() for tokentree in fulltokenlist])

    logging.info('Replacements:')
    for r in replacements:
        logging.info(f'{r} -> {replacements[r]}')

    t1 = time.time()

    print(f'Total evaluation time: {(t1 - t0):.2f} s')
