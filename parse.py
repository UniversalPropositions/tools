import multiprocessing
import stanza
import time
import argparse
import stanza
from multiprocessing import Pool
#from torch.multiprocessing import Pool, Process, set_start_method
import torch
from stanza.utils.conll import CoNLL
import json
import logging
import impl.utils as utils
from random import randrange
import os

logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./logs/parse.log"),
    logging.StreamHandler()
  ]
)

LINESEP = "\n"

nlp = None

#torch.set_num_threads(1)

def doc2conll_text(doc):
  doc_conll = CoNLL.doc2conll(doc)
  for sentence in doc_conll:
    for i, line in enumerate(sentence):
      seg = line.split("\r")
      if len(seg[0].split("-")) == 2:
        del sentence[i]
  return "\n\n".join("\n".join(line for line in sentence)
                      for sentence in doc_conll) + "\n\n"

def process_batch(batch_data):
  s1 = time.time()
  global nlp

  index = batch_data["index"]

  if not nlp:
    current_process = int(multiprocessing.current_process().name.split('-')[1]) - 1
    gpu = batch_data["gpu"]
    if gpu:
      device = current_process % torch.cuda.device_count()
      utils.set_cuda_device(device)
    else:
      device = "cpu"
    lang = batch_data["lang"]
    nlp = stanza.Pipeline(lang, processors='tokenize,pos,lemma,depparse', use_gpu=gpu, pos_batch_size=1000)
    logging.info(f'Initializing NLP batch: {index}, process: {current_process}, device: {device}')
  
  data = batch_data["data"]
  processed = nlp(data)

  result = {
    "index": index,
    "data": processed
  }
  s2 = time.time()
  logging.info(f'Processing NLP {index} time: {s2-s1} seconds')
  return result

def process_language(config, pipeline, lang):
  
  stanza.download(lang)

  input_file = "./data/" + pipeline + "/bitext_raw/" + pipeline + "." + lang + ".txt"

  with open(input_file, "r", encoding="utf-8") as f:
    sentences = f.read().split(LINESEP)

  documents = [stanza.Document([], text=d) for d in sentences]

  batches = []

  processes = config["params"]["processes"]
  batch_size = config["params"]["batch_size"]
  gpu = config["params"]["gpu"]

  counter = 0
  for i in range(0, len(documents), batch_size):
    counter += 1
    start = i
    end = start + batch_size
    batches.append({
      "index": counter,
      "data": documents[start:end],
      "lang": lang,
      "gpu": gpu
    })
    
  pool = Pool(processes)
  result = pool.map(process_batch, batches)

  sorted_result = sorted(result, key=lambda d: d['index']) 

  #tokenized sentences
  asentences = []
  sentences = []
  for s in sorted_result:
    for d in s['data']:
      atokens = []
      #it should be always one sentence, we do not need to care about it
      for sent in d.sentences:
        for token in sent.tokens:
          atokens.append(token.text)
      asentence = " ".join(atokens)
      tokens = []
      for sent in d.sentences:
        for word in sent.words:
          tokens.append(word.text)
      sentence = " ".join(tokens)

      asentences.append(asentence)
      sentences.append(sentence)

  folder_parsed = "./data/" + args.pipeline +  "/parsed"
  folder_tokenized = "./data/" + args.pipeline +  "/tokenized"
  os.makedirs(folder_parsed, exist_ok = True)
  os.makedirs(folder_tokenized, exist_ok = True)
  
  file_parsed = folder_parsed + "/" + args.pipeline + "." + lang + ".parse.conllu"
  file_tokenized = folder_tokenized + "/" + args.pipeline + "." + lang + ".tokenized.txt"
    
  with open(file_tokenized, 'w', encoding='utf8') as f:
    f.write('\n'.join(sentences))

  counter = 0
  with open(file_parsed, 'w', encoding='utf8') as f:
    for s in sorted_result:
      for d in s['data']:
        counter += 1
        f.write("# sent_id = " + str(counter) + "\n")
        if sentences[counter - 1] != asentences[counter - 1]:
          f.write("# actual text = " + asentences[counter - 1] + "\n")
        f.write("# text = " + sentences[counter - 1] + "\n")
        conllu = doc2conll_text(d)
        f.write(conllu)

if __name__ == '__main__':

  torch.multiprocessing.set_start_method('spawn')

  parser = argparse.ArgumentParser(
      description='Parsers evaluation')
  parser.add_argument('--pipeline', type=str)
  parser.add_argument('--lang', type=str)

  args = parser.parse_args()
 
  config = utils.read_config()

  if args.pipeline not in config["pipelines"]:
    raise Exception("Pipeline not available")

  cuda = utils.get_cuda_info()

  logging.info("Cuda: " + json.dumps(cuda))

  s1 = time.time()

  logging.info(f'Processing {args.lang}')
  process_language(config, args.pipeline, args.lang)

  s2 = time.time()
  logging.info(f'Total processing time: {s2-s1} seconds')