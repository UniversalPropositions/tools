import argparse
from conllu import parse_incr
import time
from simalign import SentenceAligner
from multiprocessing import Pool
import multiprocessing
import torch
import impl.utils as utils
import logging
import os
import json

LINESEP = "\n"
TYPE = 'itermax'
aligner = None

logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./logs/wordalignment.log"),
    logging.StreamHandler()
  ]
)

def save_alignments(file, batches):
  sentences = []
  for b in batches:
    for d in b["data"]:
      sentence = ' '.join([str(x[0]) + '-' + str(x[1]) for x in d])
      sentences.append(sentence)
  
  with open(file, 'w', encoding='utf8') as f:
    f.write('\n'.join(sentences))

def process_batch(batch_data):
  global aligner
  index = batch_data["index"]
  if not aligner:
    current_process = int(multiprocessing.current_process().name.split('-')[1]) - 1
    gpu = batch_data["gpu"]
    if gpu:
      device = current_process % torch.cuda.device_count()
      utils.set_cuda_device(device)
      device = "cuda:"+str(device)
    else:
      device = "cpu"
    aligner = SentenceAligner(model="bert", token_type="word", matching_methods="i", device=device)
    logging.info(f'Initializing aligner batch: {index}, process: {current_process}, device: {device}')
  
  data = batch_data["data"]
  processed = []
  
  s1 = time.time()

  for d in data:
    alignments = aligner.get_word_aligns(d["src"], d["tgt"])[TYPE]
    logging.info(f'Alignment: {d["counter"]}')
    processed.append(alignments)

  result = {
    "index": index,
    "data": processed
  }
  s2 = time.time()
  logging.info(f'Processing alignment {index} time: {s2-s1} seconds')
  
  return result

if __name__ == '__main__':

  torch.multiprocessing.set_start_method('spawn')

  parser = argparse.ArgumentParser(
      description='Parsers evaluation')
  parser.add_argument('--pipeline', type=str)

  args = parser.parse_args()

  config = utils.read_config()

  if args.pipeline not in config["pipelines"]:
      raise Exception("Pipeline not available")

  cuda = utils.get_cuda_info()

  logging.info("Cuda: " + json.dumps(cuda))

  pipeline = config["pipelines"][args.pipeline]
  source = config["sources"][pipeline["source"]]
  src_lang = source["src_lang"]
  tgt_lang = source["tgt_lang"]

  folder = "./data/" + args.pipeline

  tokenized = folder + "/tokenized"

  aligned = folder + "/aligned"

  os.makedirs(aligned, exist_ok = True)

  src_file = tokenized + "/" + args.pipeline + "." + src_lang + ".tokenized.txt"

  tgt_file = tokenized + "/" + args.pipeline + "." + tgt_lang + ".tokenized.txt"

  output_file = aligned + "/training.align"

  with open(src_file, "r", encoding="utf-8") as f:
    source_data = f.read().split(LINESEP)

  with open(tgt_file, "r", encoding="utf-8") as f:
    target_data = f.read().split(LINESEP)

  t0 = time.time()

  sentences = []
  counter = 0
  for data in zip(source_data, target_data):
    counter += 1
    source_tokens = data[0].split(" ")
    target_tokens = data[1].split(" ")
    sentences.append({
      "counter": counter,
      "src": source_tokens,
      "tgt": target_tokens
    })

  processes = config["params"]["processes"]
  batch_size = config["params"]["batch_size"]
  gpu = config["params"]["gpu"]

  counter = 0
  batches = []
  for i in range(0, len(sentences), batch_size):
    counter += 1
    start = i
    end = start + batch_size
    batches.append({
      "index": counter,
      "data": sentences[start:end],
      "gpu": gpu
    })
    
  pool = Pool(processes)
  result = pool.map(process_batch, batches)

  sorted_result = sorted(result, key=lambda d: d['index']) 
  
  save_alignments(output_file, sorted_result)

  t1 = time.time()

  logging.info(f'Total preprocessing time: {(t1 - t0):.2f} s')