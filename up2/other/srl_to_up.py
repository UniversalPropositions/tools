'''
Creates CoNLLu-p file with SRL annotations only
'''
import logging
import time
import argparse
from conllup import parse
import json
from conllup.model.tree import Tree
from conllup.model.column import Column, ColumnType
from conllup.model.token import Token
from os import path
import glob

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/srl_to_up.log"),
        logging.StreamHandler()
    ]
)


def process(input: Tree) -> Tree:
    
    output_columns = [
        Column("STANZA:ID", ColumnType.ID),
        Column("STANZA:FORM"),
        Column("STANZA:LEMMA"),
        Column("STANZA:UPOS"),
        Column("STANZA:XPOS"),
        Column("STANZA:FEATS"),
        Column("STANZA:HEAD"),
        Column("STANZA:DEPREL"),
        Column("GOLD:PRED", ColumnType.UP_PRED),
        Column("GOLD:ARGHEADS", ColumnType.UP_ARGHEADS),
    ]

    output = Tree(output_columns)
    for m in input.get_metadata():
        v = input.get_metadata(m).get_value()
        output.add_metadata(m, v)

    import copy
    for f in input.get_frames():
        output.add_frame(copy.deepcopy(f))
    
    for t in input.get_tokens():
        token = output.add_token(t.get_id())
        for c in output.get_columns_by_type(ColumnType.BASIC):
            cc = c.get_name().split(":")[1]
            token.set_attribute(c, t.get_attribute(cc))

    return output

def process_file(input, output):
    logging.info(f'Starting srl_to_up')

    t0 = time.time()

    input_columns = [
        Column("ID", ColumnType.ID),
        Column("FORM"),
        Column("LEMMA"),
        Column("UPOS"),
        Column("XPOS"),
        Column("FEATS"),
        Column("HEAD"),
        Column("DEPREL"),
        Column("UP:FLAG", ColumnType.UP_FLAG),
        Column("UP:PRED", ColumnType.UP_PRED),
        Column("UP:FRAME", ColumnType.UP_FRAME),
    ]

    try:
        counter = 0
        fi = open(input, encoding='utf8')
        fo = open(output, "w", encoding='utf8')
        for tr in parse(fi, input_columns):
            counter += 1
            print(f"sentence {counter}")
            new_tree = process(tr)
            str_tree = new_tree.to_conllup(counter == 1)
            fo.write(str_tree + "\n\n")

    except Exception as e:
        logging.error(e)
        raise e

    t1 = time.time()

    logging.info(
        f'Total srl_to_up time: {(t1 - t0):.2f} s, processed sentences: {counter}')

def srl_to_up(input, output):
    process_file(input, output)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='srl_to_up')
    parser.add_argument('--input', type=str,
                        help='Input file')
    parser.add_argument('--output', type=str,
                        help='Output conllu file')

    args = parser.parse_args()

    srl_to_up(args.input, args.output)
    
