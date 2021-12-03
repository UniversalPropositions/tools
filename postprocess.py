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

def read_file(file):
  with open(file, "r", encoding="utf-8") as f:
    return f.read().split(LINESEP)

def read_conllu(file):
  #f = open(file, "r", encoding="utf-8")
  conllu = CoNLL.conll2doc(file)
  #f.close()
  return conllu

def find_sent_to_remove_file(pipeline, lang):
  file = "./data/" + pipeline + "/parsed/" + pipeline + "." + lang + ".parsed.conllu"
  conllu = read_conllu(file)
  l = len(conllu.sentences)
  result = []
  sent_id = None
  for i, item in enumerate(conllu.sentences):
    if len(item.comments) == 0:
      result.append(sent_id)
    else:
      v = item.comments[0]
      seg = v.split(" = ")
      sent_id = int(seg[1])
  return result

def find_sent_to_remove(pipeline, src_lang, tgt_lang):
  result_src = find_sent_to_remove_file(pipeline, src_lang)
  result_tgt = find_sent_to_remove_file(pipeline, tgt_lang)
  result= list(set(result_src) | set(result_tgt))
  return result

def remove_from_text(file, sentences):
  data = read_file(file)
  output_data = []
  for i, sentence in enumerate(data):
    index = i + 1
    if index not in sentences:
      output_data.append(sentence)

  segments = file.split("/")
  segments[-1] = "_" + segments[-1]
  output_file = "/".join(segments)

  with open(output_file, 'w', encoding='utf8') as f:
    f.write('\n'.join(output_data))

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
  conllu = read_conllu(file)

  segments = file.split("/")
  segments[-1] = "_" + segments[-1]
  output_file = "/".join(segments)

  indexes_to_remove = []
  for i, item in enumerate(conllu.sentences):
    if len(item.comments) > 0:
      v = item.comments[0]
      seg = v.split(" = ")
      sent_id = int(seg[1])
      if sent_id in sentences:
        indexes_to_remove.append(i)
    else:
      indexes_to_remove.append(i)

  for i in reversed(indexes_to_remove):
    del conllu.sentences[i]

  counter = 0
  for item in conllu.sentences:
    counter += 1
    item.comments[0] = "# sent_id = " + str(counter)

  CoNLL.write_doc2conll(conllu, output_file)

def remove_sentences(pipeline, src_lang, tgt_lang, sentences):
  folder = "./data/" + pipeline + "/"
  remove_from_conllu (folder + 'parsed/'+ pipeline + "." + src_lang + ".parsed.conllu", sentences)
  remove_from_conllu (folder + 'parsed/'+ pipeline + "." + tgt_lang + ".parsed.conllu", sentences)
  remove_from_text (folder + 'tokenized/'+ pipeline + "." + src_lang + ".tokenized.txt", sentences)
  remove_from_text (folder + 'tokenized/'+ pipeline + "." + tgt_lang + ".tokenized.txt", sentences)
  remove_from_text (folder + 'aligned/training.align', sentences)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Preprocess')
  parser.add_argument('--pipeline', type=str,
                      help='Language pipeline')

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