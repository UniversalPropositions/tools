'''
Executes conversion between SRL formats, currently only one type of conversion
from: UP:PRED UP:ARGHEADS UP:ARGSPANS
to: UP:FLAG UP:PRED UP:FRAME
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
import re
import json
import pandas as pd

COLUMNS = [
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
    Column("UP:FRAME", ColumnType.UP_FRAME)
]

if not os.path.exists("./logs/"):
    os.makedirs("./logs/")
        
logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/convert_srl_format.log"),
        logging.StreamHandler()
    ]
)

def process(up: Tree) -> Tree:
    '''
    Changes SRL tree format

    :param up: UniveralPropositions conllup Tree
    :return: Conllup tree with updated format
    '''

    up.set_columns(COLUMNS)

    return up

def metaparse(sen: str, id: int) -> tuple:
    sen_txt = ''
    sen_id = ''
    sen = sen.split("\n")

    for meta_line in sen:
        if sen_txt == '':
            if re.match(r'^# [0-9]+ #', meta_line):#len(meta_line.split("#")) >= 3: #
                sen_id = int(meta_line.split("#")[1])
                sen_txt = "#".join(meta_line.split("#")[2:]).strip()
            elif meta_line.startswith("sentence-text:"):
                sen_txt =  "sentence-text:".join(meta_line.split("sentence-text:")[1:]).strip()
                continue
            elif meta_line.startswith("# text = "):
                sen_txt =  "text = ".join(meta_line.split("text = ")[1:]).strip()
                continue
            elif len(meta_line.split("sentence-text:")) > 1 and not re.match(r'^# \d # ', meta_line):
                sen_txt =  "#".join(meta_line.split("#")[1:]).strip()

        if meta_line.startswith("# srl = "):
            srl =  json.loads("srl = ".join(meta_line.split("srl = ")[1:]).strip())
        if meta_line.startswith("# sent_id = "):
            sen_id =  "sent_id = ".join(meta_line.split("sent_id = ")[1:]).strip()
    if sen_id == '':
        sen_id = id
    if sen_txt == '':
        sen_txt = " ".join(list(map(list, zip(*[x.split("\t")  for x in sen if x[0] != "#"])))[1])
    return (sen_id, sen_txt)

def process_file(up, output):
    sen_ids = []
    sen_texts = []
    logging.info(f'Starting {up}')
    t0 = time.time()
    counter = 0
    output_csv = output.replace(".conllu", ".csv")
    if path.exists(output):
        logging.info("UP output file already exists ... skipping")
    else:
        try:
            f = open(up, encoding='utf8')
            dir = path.dirname(output)
            os.makedirs(dir, exist_ok=True)
            fo = open(output, "w", encoding='utf8')
            for id, tree in enumerate(parse(f)):
                counter += 1
                if counter % 1000 == 0:
                    print(f"sentence {counter}")
                new_tree = process(tree)
                str_tree = new_tree.to_conllup(False) #do not put global.columns
                sen_id, sen_text = metaparse(str_tree, id)
                sen_texts.append(sen_text)
                sen_ids.append(sen_id)
                fo.write(str_tree + "\n\n")
        except Exception as e:
            logging.error(e)
            raise e
        df = pd.DataFrame(zip(sen_ids, sen_texts), columns=["id", "text"])
        df.to_csv(output_csv,index=False)
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

def convert_srl_format(input_up, output):
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
        description='convert_srl_format')
    parser.add_argument('--input_up', type=str,
                        help='Universal Propositions input file/folder')
    parser.add_argument('--output', type=str,
                        help='Output SRL conllu file/folder')

    args = parser.parse_args()

    convert_srl_format(args.input_up, args.output)
