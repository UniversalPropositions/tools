'''
Merges Universal Dependencies and Universal Propositions into one output file.
'''
import logging
import time
import argparse
from conllup import zip_parse
from conllup.model.tree import Tree
from conllup.model.column import Column, ColumnType
from os import path
import glob
import os

os.makedirs("./logs", exist_ok=True)

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/merge_ud_up.log"),
        logging.StreamHandler()
    ]
)


def process(ud: Tree, up: Tree) -> Tree:
    '''
    Merges universal dependencies conllup Tree object with Universal 
    Propositions conllup Tree object and returns output conllup Tree object with merged data

    :param ud: UniersalDependencies conllup Tree
    :param up: UniveralPropositions conllup Tree
    :return: Conllup tree that contains merged data
    '''
    columns = [
        Column("ID", ColumnType.ID),
        Column("FORM"),
        Column("LEMMA"),
        Column("UPOS"),
        Column("XPOS"),
        Column("FEATS"),
        Column("HEAD"),
        Column("DEPREL"),
        Column("DEPS"),
        Column("MISC"),
        Column("UP:PRED", ColumnType.UP_PRED),
        Column("UP:ARGHEADS", ColumnType.UP_ARGHEADS),
        Column("UP:ARGSPANS", ColumnType.UP_ARGSPANS)
    ]

    tree = Tree(columns)

    for m in ud.get_metadata():
        tree.add_metadata(m, ud.get_metadata(m).get_value())

    for ud_token in ud.get_tokens():

        tt = tree.add_token(ud_token.get_id())
        tt.set_attribute("FORM", ud_token.get_attribute('FORM'))
        tt.set_attribute("LEMMA", ud_token.get_attribute('LEMMA'))
        tt.set_attribute("UPOS", ud_token.get_attribute('UPOS'))
        tt.set_attribute("XPOS", ud_token.get_attribute('XPOS'))
        tt.set_attribute("FEATS", ud_token.get_attribute('FEATS'))
        tt.set_attribute("HEAD", ud_token.get_attribute('HEAD'))
        tt.set_attribute("DEPREL", ud_token.get_attribute('DEPREL'))
        tt.set_attribute("DEPS", ud_token.get_attribute('DEPS'))
        tt.set_attribute("MISC", ud_token.get_attribute('MISC'))

    for frame in up.get_frames():
        tree.add_frame(frame)

    return tree

def process_file(ud, up, output):
    logging.info(f'Starting {ud} and {up}')
    t0 = time.time()
    counter = 0
    if path.exists(output):
        logging.info("UD-UP output file already exists ... skipping")
    else:
        try:
            f1 = open(ud, encoding='utf8')
            f2 = open(up, encoding='utf8')
            dir = path.dirname(output)
            os.makedirs(dir, exist_ok=True)
            fo = open(output, "w", encoding='utf8')
            for tree in zip_parse(f1, f2):
                ud_tree = tree[0]
                up_tree = tree[1]
                counter += 1
                if counter % 1000 == 0:
                    print(f"sentence {counter}")
                new_tree = process(ud_tree, up_tree)
                str_tree = new_tree.to_conllup(counter == 1)
                fo.write(str_tree + "\n\n")
        except Exception as e:
            logging.error(e)
            raise e

        t1 = time.time()

        logging.info(
            f'Processing time: {(t1 - t0):.2f} s, processed sentences: {counter}')

def process_folders(ud, up, out):
    files = glob.glob(f'{up}/**/*.conllu*', recursive=True)
    for up_file in files:
        ud_file = up_file.replace(up, ud).replace("-up-", "-ud-").replace(".conllup", ".conllu")
        out_file = up_file.replace(up, out).replace("-up-", "-ud-up-")
        process_file(ud_file, up_file, out_file)

def merge_ud_up(input_ud, input_up, output):
    if path.isdir(input_ud) and path.isdir(input_up):
        if not os.path.exists(output):
            os.makedirs(output, exist_ok=True)
        process_folders(input_ud, input_up, output)
    elif path.isfile(input_ud) and path.isfile(input_up):
        process_file(input_ud, input_up, output)
    else:
        msg = "Do not mix files and folders as input parameters"
        logging.error(msg)
        raise Exception(msg)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='merge_ud_up')
    parser.add_argument('--input_ud', type=str,
                        help='Universal Dependencies input file/folder')
    parser.add_argument('--input_up', type=str,
                        help='Universal Propositions input file/folder')
    parser.add_argument('--output', type=str,
                        help='Output SRL conllu file/folder')

    args = parser.parse_args()

    merge_ud_up(args.input_ud, args.input_up, args.output)
