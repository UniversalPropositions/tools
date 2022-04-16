'''
Script fixes word_alignment results using parse results for tokens that contain more than one word
'''

import argparse
import time
import json
from utils import read_config
import logging
from stanza.utils.conll import CoNLL

LINESEP = "\n"

logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./logs/fix-align.log"),
    logging.StreamHandler()
  ]
)

def read_large_data(filename):
  """
  To get one sentence at a time from a big file
  :param filename: path to the filename
  :return: Yield one sentence at a time
  """
  with open(filename) as f:
      data = f.readlines()

  sen = []
  for line in data:
      if line == "\n" or line == "---\n":
          if sen != []:
              yield sen
          sen = []
      else:
          sen.append(line.strip())
  if sen != []:
      yield sen
      
def read_file(file):
  with open(file, "r", encoding="utf-8") as f:
    return f.read().split(LINESEP)

def process_lang(pipeline, lang):
  map = {}
  parse_file = f'./data/{pipeline}/parsed/_{pipeline}.{lang}.parsed.conllu'
  sentence_number = 0
  for sentence in read_large_data(parse_file):
    token_number = 0
    token_original = 0
    for t in sentence:
      if not t.startswith("#"):
        segments = t.split("\t")
        text = segments[1]
        words = text.count(" ") + 1
        if words > 1:
          for w in range(0, words):
            if sentence_number not in map:
              map[sentence_number] = {}
            map[sentence_number][token_number + w] = token_original
          token_number += words - 1
        else:
          if token_number > token_original:
            if sentence_number not in map:
              map[sentence_number] = {}
            map[sentence_number][token_number] = token_original
        token_number += 1
        token_original += 1
    sentence_number += 1
  return map

def process(pipeline, src_lang, tgt_lang):
  try:
    align_file = f'./data/{pipeline}/aligned/__training.align'
    output_file = f'./data/{pipeline}/aligned/___training.align'

    output = open(output_file, 'w', encoding='utf8')

    src_map = process_lang(pipeline, src_lang)
    tgt_map = process_lang(pipeline, tgt_lang)

    logging.info("src: " + json.dumps(src_map, indent=2))
    logging.info("tgt: " + json.dumps(tgt_map, indent=2))

    alignments = read_file(align_file)
    new_alignments = []

    for i, a in enumerate(alignments):
      if len(a) == 0:
        continue
      segments = a.split(" ")
      new_segments = []
      for s in segments:
        split = s.split("-")
        src = int(split[0])
        tgt = int(split[1])
        if i in src_map:
          if src in src_map[i]:
            src = src_map[i][src]
        if i in tgt_map:
          if tgt in tgt_map[i]:
            tgt = tgt_map[i][tgt]
        new_segments.append(f'{src}-{tgt}')
      new_alignments.append(' '.join(new_segments))

    for na in new_alignments:
      output.write(na+"\n")
    output.close()
  except Exception as e:
    logging.error(e)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='fix-align')
  parser.add_argument('--pipeline', type=str,
                      help='Language pipeline')

  args = parser.parse_args()

  logging.info(f'Starting postprocessing: {args.pipeline}')

  t0 = time.time()

  try:

    config = read_config()

    args = parser.parse_args()

    t0 = time.time()

    if args.pipeline not in config["pipelines"]:
      raise Exception("Pipeline not available")

    pipeline = config["pipelines"][args.pipeline]
    source = config["sources"][pipeline["source"]]
    datasets = source["datasets"]
    src_lang = source["src_lang"]
    tgt_lang = source["tgt_lang"]

    process(args.pipeline, src_lang, tgt_lang)

  except Exception as e:
    logging.error(e)
  
  t1 = time.time()

  logging.info(f'Total postprocessing time: {(t1 - t0):.2f} s')