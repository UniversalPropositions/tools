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
    logging.FileHandler("./logs/postprocess-spade.log"),
    logging.StreamHandler()
  ]
)

def get_verb(srl, id):
  for verb in srl["verbs"]:
    if verb["verb"][0] == id:
      return verb
  return None

def create_dep(args):
  #AM-DIS:1|A1:3|AM-NEG:5|A2:6
  tokens = []
  for arg in args:
    name = arg[1]
    pos = arg[0]
    tokens.append(f'{name}:{pos}')
  return '|'.join(tokens)

def create_span(args):
  #AM-DIS:1|A1:3|AM-NEG:5|A2:6-10
  tokens = []
  for arg in args:
    name = arg[1]
    start = arg[2]
    end = arg[3]
    if start == end:
      tokens.append(f'{name}:{start}')
    else:
      tokens.append(f'{name}:{start}-{end}')
  return '|'.join(tokens)

def process(source, ud, spade):
  definition = ["ID", "UP:PREDS", "UP:DEPARGS", "UP:SPANARGS"]
  
  tree = Tree(definition)
  
  file_name = source
  sent_id = ud.metadata['sent_id'].value
  text = ud.metadata['text'].value
  span_srl = spade.metadata["span_srl"].value

  metadata = tree.create_metadata("source_sent_id")
  metadata.set_value(f"conllu http://hdl.handle.net/11234/1-4611 {file_name} {sent_id}")
  
  metadata = tree.create_metadata("sent_id")
  metadata.set_value(f"{sent_id}")
  
  metadata = tree.create_metadata("text")
  metadata.set_value(text)

  for t in spade.tokens:

    token = spade.tokens[t]

    id = int(t)
    srl = json.loads(span_srl)

    verb = get_verb(srl, id)

    if verb:
      predicate = verb["verb"][1]
      dep = create_dep(verb["arguments"])
      span = create_span(verb["arguments"])
    else:
      predicate = "_"
      dep = "_"
      span = "_"

    tt = tree.create_token(id)
    tt.set_attribute("ID", token.attributes['ID'])
    tt.set_attribute("UP:PREDS", predicate)
    tt.set_attribute("UP:DEPARGS", dep)
    tt.set_attribute("UP:SPANARGS", span)

  return tree

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Preprocess-spade')
  parser.add_argument('--source', type=str,
                      help='UD source file description')
  parser.add_argument('--input_ud', type=str,
                      help='Input file with ud result')
  parser.add_argument('--input_spade', type=str,
                      help='Input file with spade result')
  parser.add_argument('--output', type=str,
                      help='Output conllu file')

  args = parser.parse_args()

  logging.info(f'Starting postprocess-spade')

  t0 = time.time()

  try:
    counter = 0
    f1 = open(args.input_ud, encoding='utf8')
    f2 = open(args.input_spade, encoding='utf8')
    fo = open(args.output, "w", encoding='utf8')
    for tree in zip_parse(f1, f2):
      ud_tree = tree[0]
      spade_tree = tree[1]
      counter += 1
      new_tree = process(args.source, ud_tree, spade_tree)
      str_tree = new_tree.to_conllup()
      fo.write(str_tree + "\n\n")

  except Exception as e:
    logging.error(e)
  
  t1 = time.time()

  logging.info(f'Total postprocess-spade time: {(t1 - t0):.2f} s, processed sentences: {counter}')