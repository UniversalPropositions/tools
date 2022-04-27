'''
Creates CoNLLu-p file with SRL annotations only
'''
import logging
import time
import argparse
from conllup import zip_parse
import json
from conllup.model.tree import Tree
from conllup.model.column import Column, ColumnType
from conllup.model.frame import Frame
from conllup.model.predicate import Predicate
from conllup.model.argument import Argument
from os import path
import glob

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/spade_to_up.log"),
        logging.StreamHandler()
    ]
)


def process(source: str, ud: Tree, spade: Tree) -> Tree:
    '''
    Combines CoNLL-U Plus UniversalDependencies and Spade trees into on Tree with 4 attributes only

    :param source: string to be placed inside source_sent_id metadata
    :param ud: UniversalDependencies CoNLL-U Plus file
    :param spade: Spade CoNNL-U file
    :return: output CoNNL-U Plus tree
    '''

    columns = [
        Column("ID", ColumnType.ID),
        Column("UP:PRED", ColumnType.UP_PRED),
        Column("UP:ARGHEADS", ColumnType.UP_ARGHEADS),
        Column("UP:ARGSPANS", ColumnType.UP_ARGSPANS)
    ]

    tree = Tree(columns)

    sent_id = ud.get_metadata('sent_id').get_value()
    span_srl = spade.get_metadata("span_srl").get_value()
    srl = json.loads(span_srl)

    tree.add_metadata(
        "source_sent_id", f"conllu http://hdl.handle.net/11234/1-4611 {source} {sent_id}")

    tree.add_metadata("sent_id", f"{sent_id}")

    text = ""
    for t in ud.get_tokens():
        tree.add_token(t.get_id())
        text += "_ "

    text = text.strip()
    tree.add_metadata("text", text)

    for verb in srl["verbs"]:
        predicate = verb["verb"]
        frame = Frame()
        tree.add_frame(frame)
        frame.set_predicate(Predicate(predicate[1], token=predicate[0]))
        for argument in verb["arguments"]:
            frame.add_argument(
                Argument(argument[1], head=argument[0], start=argument[2], end=argument[3]))

    return tree

def process_file(source, input_ud, input_spade, output):
    logging.info(f'Starting spade_to_up')

    t0 = time.time()

    try:
        counter = 0
        f1 = open(input_ud, encoding='utf8')
        f2 = open(input_spade, encoding='utf8')
        fo = open(output, "w", encoding='utf8')
        for tr in zip_parse(f1, f2):
            ud_tree = tr[0]
            spade_tree = tr[1]
            counter += 1
            print(f"sentence {counter}")
            new_tree = process(source, ud_tree, spade_tree)
            str_tree = new_tree.to_conllup(counter == 1)
            fo.write(str_tree + "\n\n")

    except Exception as e:
        logging.error(e)
        raise e

    t1 = time.time()

    logging.info(
        f'Total spade_to_up time: {(t1 - t0):.2f} s, processed sentences: {counter}')

def process_folders(source, ud, spade, out):
    files = glob.glob(f'{spade}/**/*.spade.conllu', recursive=True)
    for spade_file in files:
        ud_file = spade_file.replace(spade, ud).replace(".spade.conllu", "")
        out_file = spade_file.replace(spade, out).replace("-ud-", "-up-").replace(".spade.conllu", "")
        process_file(source, ud_file, spade_file, out_file)

def spade_to_up(source, input_ud, input_spade, output):
    if path.isdir(input_ud) and path.isdir(input_spade) and path.isdir(output):
        process_folders(source, input_ud, input_spade, output)
    elif path.isfile(input_ud) and path.isfile(input_spade):
        process_file(source, input_ud, input_spade, output)
    else:
        msg = "Do not mix files and folders as input parameters"
        logging.error(msg)
        raise Exception(msg)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='spade_to_up')
    parser.add_argument('--source', type=str,
                        help='UD source file description')
    parser.add_argument('--input_ud', type=str,
                        help='Input file with ud result')
    parser.add_argument('--input_spade', type=str,
                        help='Input file with spade result')
    parser.add_argument('--output', type=str,
                        help='Output conllu file')

    args = parser.parse_args()

    spade_to_up(args.source, args.input_ud, args.input_spade, args.output)
    
