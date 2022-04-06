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
from conllup.model.column import Column, ColumnType
from conllup.model.frame import Frame
from conllup.model.predicate import Predicate
from conllup.model.argument import Argument

logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./logs/postprocess-spade.log"),
    logging.StreamHandler()
  ]
)

def process(source, ud, spade):

  columns = [
    Column("ID", ColumnType.ID),
    Column("UP:PREDS", ColumnType.UP_PREDS),
    Column("UP:DEPARGS", ColumnType.UP_DEPARGS),
    Column("UP:SPANARGS", ColumnType.UP_SPANARGS)
  ]
  
  tree = Tree(columns)
  
  sent_id = ud.metadata['sent_id'].value
  #text = ud.metadata['text'].value
  span_srl = spade.metadata["span_srl"].value
  srl = json.loads(span_srl)

  tree.add_metadata("source_sent_id", f"conllu http://hdl.handle.net/11234/1-4611 {source} {sent_id}")
  
  tree.add_metadata("sent_id", f"{sent_id}")

  text = ""
  for t in ud.tokens:
    tree.add_token(t)
    text += "_ "

  text = text.strip()
  tree.add_metadata("text", text)

  for verb in srl["verbs"]:
    predicate = verb["verb"]
    frame = Frame()
    tree.add_frame(frame)
    frame.set_predicate(Predicate(predicate[1], token=predicate[0]))
    for argument in verb["arguments"]:
      frame.add_argument(Argument(argument[1], head=argument[0], start=argument[2], end=argument[3]))

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
    for tr in zip_parse(f1, f2):
      ud_tree = tr[0]
      spade_tree = tr[1]
      counter += 1
      new_tree = process(args.source, ud_tree, spade_tree)
      str_tree = new_tree.to_conllup()
      fo.write(str_tree + "\n\n")

  except Exception as e:
    logging.error(e)
    raise e
  
  t1 = time.time()

  logging.info(f'Total postprocess-spade time: {(t1 - t0):.2f} s, processed sentences: {counter}')

