'''
Script removes from parsed, tokenized, aligned datasets lines that were parsed by stanza 
into more than one sentence. It creates new files with _ at the beginning of the file name.
'''

import argparse
import time
import re
import impl.utils as utils
import logging
import glob
import os
from stanza.utils.conll import CoNLL

LINESEP = "\n"

logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./logs/postprocess.log"),
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

def find_sent_to_remove_file(pipeline, lang):
  file = "./data/" + pipeline + "/parsed/" + pipeline + "." + lang + ".parsed.conllu"
  result = []
  sentence_number = 0
  for sentence in read_large_data(file):
    if len(sentence) > 0:
      sent = sentence[0]
      if sent.startswith("# sent_id = "):
        segments = sent.split(" = ")
        seg = segments[1]
        sentence_number = int(seg)
      else:
        result.append(sentence_number)
  return result

def find_sent_to_remove(pipeline, src_lang, tgt_lang):
  result_src = find_sent_to_remove_file(pipeline, src_lang)
  result_tgt = find_sent_to_remove_file(pipeline, tgt_lang)
  result= list(set(result_src) | set(result_tgt))
  return result

def remove_from_text(file, sentences):
  try:
    data = read_file(file)
    output_data = []
    index = 0
    for sentence in data:
      index += 1
      if index not in sentences:
        output_data.append(sentence)

    segments = file.split("/")
    segments[-1] = "_" + segments[-1]
    output_file = "/".join(segments)

    with open(output_file, 'w', encoding='utf8') as f:
      f.write('\n'.join(output_data))
  except Exception as e:
    logging.error(e)

def remove_from_srl(file, sentences):
  try:
    segments = file.split("/")
    segments[-1] = "_" + segments[-1]
    output_file = "/".join(segments)

    output = open(output_file, 'w', encoding='utf8')

    sentence_number = 0
    for sentence in read_large_data(file):
      sentence_number += 1
      if sentence_number not in sentences:
        for s in sentence:
          output.write(s+"\n")
        output.write("\n")
    output.close()
  except Exception as e:
    logging.error(e)

def doc2conll_text(doc):
  doc_conll = CoNLL.doc2conll(doc)
  for sentence in doc_conll:
    for i, line in enumerate(sentence):
      seg = line.split("\r")
      if len(seg[0].split("-")) == 2:
        del sentence[i]
  return "\n\n".join("\n".join(line for line in sentence)
                      for sentence in doc_conll) + "\n\n"

def remove_from_conllu(file, sentences):
  try:
    segments = file.split("/")
    segments[-1] = "_" + segments[-1]
    output_file = "/".join(segments)

    output = open(output_file, 'w', encoding='utf8')

    sentence_number = 0
    added_counter = 0
    for sentence in read_large_data(file):
      if len(sentence) > 0:
        sent = sentence[0]
        if sent.startswith("# sent_id = "):
          segments = sent.split(" = ")
          seg = segments[1]
          sentence_number = int(seg)
          if sentence_number not in sentences:
            added_counter += 1
            sentence[0] = "# sent_id = " + str(added_counter)
            for s in sentence:
              output.write(s+"\n")
            output.write("\n")
    output.close()
  except Exception as e:
    logging.error(e)

def remove_sentences(pipeline, src_lang, tgt_lang, sentences):
  folder = "./data/" + pipeline + "/"
  logging.info("Updating src parsed")
  remove_from_conllu (folder + 'parsed/'+ pipeline + "." + src_lang + ".parsed.conllu", sentences)
  logging.info("Updating tgt parsed")
  remove_from_conllu (folder + 'parsed/'+ pipeline + "." + tgt_lang + ".parsed.conllu", sentences)
  logging.info("Updating src tokenized")
  remove_from_text (folder + 'tokenized/'+ pipeline + "." + src_lang + ".tokenized.txt", sentences)
  logging.info("Updating tgt tokenized")
  remove_from_text (folder + 'tokenized/'+ pipeline + "." + tgt_lang + ".tokenized.txt", sentences)
  logging.info("Updating aligned")
  remove_from_text (folder + 'aligned/training.align', sentences)
  logging.info("Updating src srl")
  remove_from_srl (folder + 'tokenized/'+ pipeline + "." + src_lang + ".tokenized.txt.srl", sentences)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Preprocess')
  parser.add_argument('--pipeline', type=str,
                      help='Language pipeline', default="en-fr-200k")

  args = parser.parse_args()

  logging.info(f'Starting postprocessing: {args.pipeline}')

  t0 = time.time()

  try:

    config = utils.read_config()

    args = parser.parse_args()

    t0 = time.time()

    if args.pipeline not in config["pipelines"]:
      raise Exception("Pipeline not available")

    pipeline = config["pipelines"][args.pipeline]
    source = config["sources"][pipeline["source"]]
    datasets = source["datasets"]
    src_lang = source["src_lang"]
    tgt_lang = source["tgt_lang"]

    sentences = find_sent_to_remove(args.pipeline, src_lang, tgt_lang)

    remove_sentences(args.pipeline, src_lang, tgt_lang, sentences)

  except Exception as e:
    logging.error(e)
  
  t1 = time.time()

  logging.info(f'Total postprocessing time: {(t1 - t0):.2f} s')