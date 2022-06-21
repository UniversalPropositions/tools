'''
Fixes predicate/sense position and argument tokens for sentences 
with some additional tokens like for example: 14.1
'''
import logging
import time
import argparse
from conllup import parse
from conllup.model.tree import Tree
from conllup.model.column import Column, ColumnType
from os import path
import glob
import os

if not os.path.exists("./logs/"):
    os.makedirs("./logs/")
        
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/fix_up.log"),
        logging.StreamHandler()
    ]
)

def process(up: Tree) -> Tree:
    '''
    Updates SRL predicate/sense and tokens for arguments

    :param up: UniveralPropositions conllup Tree
    :return: Conllup tree with updated positions
    '''
    token_map = {}
    index = 0
    diff = 0
    tokens = up.get_tokens()
    max_id = None
    for token in tokens:
        token_map[token.get_id()] = tokens[index - diff].get_id()
        if "." in token.get_id():
           diff += 1
        index += 1
        max_id = token.get_id()
    max_id = int(max_id)
    for i in range(max_id + 1, max_id + 11):
        token_map[str(i)] = str(i - diff)

    for frame in up.get_frames():
        predicate = frame.get_predicate()
        prev = predicate.get_token()
        new = token_map[prev]
        if prev != new:
            predicate.set_token(new)
        for argument in frame.get_arguments():
            prev = argument.get_head()
            if prev is not None and prev != 0:
                new = token_map[prev]
                if prev != new:
                    argument.set_head(new)
            prev = argument.get_start()
            if prev is not None and prev != 0:
                new = token_map[prev]
                if prev != new:
                    argument.set_start(new)
            prev = argument.get_end()
            if prev is not None and prev != 0:
                new = token_map[prev]
                if prev != new:
                    argument.set_end(new)
    return up

def process_file(up, output):
    logging.info(f'Starting {up}')
    t0 = time.time()
    counter = 0
    if path.exists(output):
        logging.info("UP output file already exists ... skipping")
    else:
        try:
            f = open(up, encoding='utf8')
            dir = path.dirname(output)
            os.makedirs(dir, exist_ok=True)
            fo = open(output, "w", encoding='utf8')
            for tree in parse(f):
                counter += 1
                if counter % 1000 == 0:
                    print(f"sentence {counter}")
                if counter == 363:
                    print("OK")
                new_tree = process(tree)
                str_tree = new_tree.to_conllup(counter == 1)
                fo.write(str_tree + "\n\n")
        except Exception as e:
            logging.error(e)
            raise e

        t1 = time.time()

        logging.info(
            f'Processing time: {(t1 - t0):.2f} s, processed sentences: {counter}')

def process_folders(up, out):
    files = glob.glob(f'{up}/**/*.conllup', recursive=True)
    for up_file in files:
        out_file = up_file.replace(up, out).replace(".conllup", ".conllu")
        try:
            process_file(up_file, out_file)
        except Exception as e:
            logging.error(e)

def fix_up(input_up, output):
    if path.isdir(input_up):
        if not os.path.exists(output):
            os.makedirs(output, exist_ok=True)
        process_folders(input_up, output)
    elif path.isfile(input_up):
        process_file(input_up, output)
    else:
        msg = "Do not mix files and folders as input parameters"
        logging.error(msg)
        raise Exception(msg)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='fix_up')
    parser.add_argument('--input_up', type=str,
                        help='Universal Propositions input file/folder')
    parser.add_argument('--output', type=str,
                        help='Output SRL conllup file/folder')

    args = parser.parse_args()

    fix_up(args.input_up, args.output)
