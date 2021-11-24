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

def doc2conll_text(doc):
  doc_conll = CoNLL.doc2conll(doc)
  for sentence in doc_conll:
    for i, line in enumerate(sentence):
      seg = line.split("\r")
      if len(seg[0].split("-")) == 2:
        del sentence[i]
  return "\n\n".join("\n".join(line for line in sentence)
                      for sentence in doc_conll) + "\n\n"

def check_if_result(pipeline, lang, index):
  folder_tokenized = "./data/" + pipeline +  "/tokenized/tmp"
  s = ""
  if index:
    s = str(index).zfill(4) + "."
  file_tokenized = folder_tokenized + "/" + pipeline + "." + lang + ".tokenized." + s + "txt"
  return os.path.isfile(file_tokenized)

def process_batch(batch_data):
  s1 = time.time()
  global nlp

  index = batch_data["index"]
  processes = batch_data["processes"]
  logging.info(f'Starting batch {index}')
  batch_size = batch_data["batch_size"]
  batch_save = batch_data["save"]
  pipeline = batch_data["pipeline"]
  lang = batch_data["lang"]

  if batch_save:
    available = check_if_result(pipeline, lang, index)
    if available:
      logging.info(f'Skipping batch {index}')
      return None

  if not nlp:
    if processes > 1:
      current_process = int(multiprocessing.current_process().name.split('-')[1]) - 1
    else:
      current_process = 1
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
  logging.info(f'Processing batch {index} time: {s2-s1} seconds')

  if batch_save:
    save(pipeline, lang, [result], index, batch_size)
    return None
  else:
    return result

def process_language(config, pipeline, lang):
  
  stanza.download(lang)

  input_file = "./data/" + pipeline + "/bitext_raw/" + pipeline + "." + lang + ".txt"

  with open(input_file, "r", encoding="utf-8") as f:
    sentences = f.read().split(LINESEP)

  limit = config["params"]["limit"]

  if limit == 0 or len(sentences) < limit:
    limit = len(sentences)

  documents = [stanza.Document([], text=d) for d in sentences[0:limit]]

  batches = []

  processes = config["params"]["processes"]
  batch_size = config["params"]["batch_size"]
  batch_save = config["params"]["batch_save"]
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
      "gpu": gpu,
      "save": batch_save,
      "pipeline": pipeline,
      "batch_size": batch_size,
      "processes": processes
    })
  
  if processes > 1:
    pool = Pool(processes)
    result = pool.map(process_batch, batches)
  else:
    result = []
    for batch in batches:
      batch_result = process_batch(batch)
      result.append(batch_result)

  if not batch_save:

    sorted_result = sorted(result, key=lambda d: d['index']) 

    save(pipeline, lang, sorted_result)

def save(pipeline, lang, sorted_result, index = None, batch_size = None):
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

  s = ""
  if index:
    s = "/tmp"
  folder_parsed = "./data/" + pipeline +  "/parsed" + s
  folder_tokenized = "./data/" + pipeline +  "/tokenized" + s
  os.makedirs(folder_parsed, exist_ok = True)
  os.makedirs(folder_tokenized, exist_ok = True)
  
  s = ""
  if index:
    s = str(index).zfill(4) + "."

  file_parsed = folder_parsed + "/" + pipeline + "." + lang + ".parsed." + s + "conllu"
  file_tokenized = folder_tokenized + "/" + pipeline + "." + lang + ".tokenized." + s + "txt"
    
  with open(file_tokenized, 'w', encoding='utf8') as f:
    f.write('\n'.join(sentences))

  counter = 0
  with open(file_parsed, 'w', encoding='utf8') as f:
    for s in sorted_result:
      for d in s['data']:
        counter += 1
        if index and batch_size:
          sent = (index - 1) * batch_size + counter
        else:
          sent = counter
        f.write("# sent_id = " + str(sent) + "\n")
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