'''

'''

import logging
import time
import argparse
from conllup import zip_parse
import json
from conllup.model.tree import Tree
from conllup.model.tree import Token
from conllup.model.tree import Metadata

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
  definition = ["ID", "FORM", "LEMMA", "UPOS", "XPOS", "FEATS", "HEAD", "DEPREL", "DEPS", "MISC", "UP:PREDS", "UP:DEPARGS", "UP:SPANARGS"]
  
  tree = Tree(definition)
  
  metadata = tree.create_metadata("source_sent_id")
  metadata.set_value(up.metadata["source_sent_id"].value)

  metadata = tree.create_metadata("sent_id")
  metadata.set_value(up.metadata["sent_id"].value)

  metadata = tree.create_metadata("text")
  metadata.set_value(up.metadata["text"].value)

  for t in ud.tokens:

    ud_token = ud.tokens[t]
    up_token = up.tokens[t]

    id = int(t)

    tt = tree.create_token(id)
    tt.set_attribute("ID", ud_token.attributes['ID'])
    tt.set_attribute("FORM", ud_token.attributes['FORM'])
    tt.set_attribute("LEMMA", ud_token.attributes['LEMMA'])
    tt.set_attribute("UPOS", ud_token.attributes['UPOS'])
    tt.set_attribute("XPOS", ud_token.attributes['XPOS'])
    tt.set_attribute("FEATS", ud_token.attributes['FEATS'])
    tt.set_attribute("HEAD", ud_token.attributes['HEAD'])
    tt.set_attribute("DEPREL", ud_token.attributes['DEPREL'])
    tt.set_attribute("DEPS", ud_token.attributes['DEPS'])
    tt.set_attribute("MISC", ud_token.attributes['MISC'])

    tt.set_attribute("UP:PREDS", up_token.attributes["UP:PREDS"])
    tt.set_attribute("UP:DEPARGS", up_token.attributes["UP:DEPARGS"])
    tt.set_attribute("UP:SPANARGS", up_token.attributes["UP:SPANARGS"])

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