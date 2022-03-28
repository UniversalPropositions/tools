'''

'''

import logging
import time
import argparse
from conllup import zip_parse
import json
from conllup.model.tree import Tree
from conllup.model.metadata import Metadata
from conllup.model.column import Column, ColumnType

logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./logs/merge_ud_srl.log"),
    logging.StreamHandler()
  ]
)

def process(ud, up):

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
            Column("UP:PREDS", ColumnType.UP_PREDS),
            Column("UP:DEPARGS", ColumnType.UP_DEPARGS),
            Column("UP:SPANARGS", ColumnType.UP_SPANARGS)
        ]

  tree = Tree(columns)
  
  metadata = tree.add_metadata("source_sent_id", up.metadata["source_sent_id"].value)
  metadata = tree.add_metadata("sent_id", up.metadata["sent_id"].value)
  metadata = tree.add_metadata("text", up.metadata["text"].value)

  for t in ud.tokens:

    ud_token = ud.tokens[t]
    up_token = up.tokens[t]

    id = int(t)

    tt = tree.add_token(id)
    tt.set_attribute("FORM", ud_token.attributes['FORM'])
    tt.set_attribute("LEMMA", ud_token.attributes['LEMMA'])
    tt.set_attribute("UPOS", ud_token.attributes['UPOS'])
    tt.set_attribute("XPOS", ud_token.attributes['XPOS'])
    tt.set_attribute("FEATS", ud_token.attributes['FEATS'])
    tt.set_attribute("HEAD", ud_token.attributes['HEAD'])
    tt.set_attribute("DEPREL", ud_token.attributes['DEPREL'])
    tt.set_attribute("DEPS", ud_token.attributes['DEPS'])
    tt.set_attribute("MISC", ud_token.attributes['MISC'])

  for frame in up.get_frames():
    tree.add_frame(frame)

  return tree

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='merge-ud-srl')
  parser.add_argument('--input_ud', type=str,
                      help='Universal Dependencies input file')
  parser.add_argument('--input_up', type=str,
                      help='Universal Propositions input file')
  parser.add_argument('--output', type=str,
                      help='Output SRL conllu file')

  args = parser.parse_args()

  logging.info(f'Starting ...')

  t0 = time.time()

  try:
    counter = 0
    f1 = open(args.input_ud, encoding='utf8')
    f2 = open(args.input_up, encoding='utf8')
    fo = open(args.output, "w", encoding='utf8')
    for tree in zip_parse(f1, f2):
      ud_tree = tree[0]
      up_tree = tree[1]
      counter += 1
      new_tree = process(ud_tree, up_tree)
      str_tree = new_tree.to_conllup()
      fo.write(str_tree + "\n\n")

  except Exception as e:
    logging.error(e)
  
  t1 = time.time()

  logging.info(f'Total processing time: {(t1 - t0):.2f} s, processed sentences: {counter}')