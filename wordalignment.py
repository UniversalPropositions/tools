'''
Scripts executes word alignments on two parallel text files for source and target language.
Input files are read from ./data/[pipeline]/tokenized.
Output file is stored in ./data/[pipeline]/aligned/training.align file.
'''
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

def check_if_result(pipeline: str, index: int):
  '''
  Checks if temporary result is available in the file system for a given pipeline, 
  language and batch index

  :param pipeline: processing pipeline from config.json file
  :param lang: source or target language identifier
  :param index: batch index to be checked
  :return: information if file is present or not
  '''
  folder = "./data/" + pipeline +  "/aligned/tmp"
  s = ""
  if index:
    s = str(index).zfill(4) + "."
  output_file = folder + "/training." + s + "align"
  return os.path.isfile(output_file)

def save_alignments(pipeline: str, batches: dict, index: int = None, batch_size: int = None):
  '''
  Saves alignment results into file

  :param pipeline: processed pipeline name from config.json file
  :param batches: Word alignment results returned by batch processing to be stored in output file
  :index: batch number (applies only when config.json parameter batch_save=true)
  :batch_size: batch size (applies only when config.json parameter batch_save=true)
  '''
  sentences = []
  for b in batches:
    for d in b["data"]:
      sentence = ' '.join([str(x[1]) + '-' + str(x[0]) for x in d])
      sentences.append(sentence)

  s = ""
  if index:
    s = "/tmp"

  folder = "./data/" + pipeline + "/aligned" + s
  os.makedirs(folder, exist_ok = True)
  
  s = ""
  if index:
    s = str(index).zfill(4) + "."

  output_file = folder + "/training." + s + "align"

  with open(output_file, 'w', encoding='utf8') as f:
    f.write('\n'.join(sentences))

def process_batch(batch_data: dict) -> dict:
  '''
  Processes single word alignment batch

  :param batch_data: dictionary containing all information required to process a given batch
  :return: dictionary with batch processing result, in case batch_save is set to true in 
          config.json None is returned and then merge-align.py script must be used to merge partial
          results into one file
  '''
  global aligner

  index = batch_data["index"]
  batch_size = batch_data["batch_size"]
  batch_save = batch_data["save"]
  pipeline = batch_data["pipeline"]

  if batch_save:
    available = check_if_result(pipeline, index)
    if available:
      logging.info(f'Skipping batch {index}')
      return None

  if not aligner:
    if processes > 1:
      current_process = int(multiprocessing.current_process().name.split('-')[1]) - 1
    else:
      current_process = 1
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
    try:
      alignments = []
      alignments = aligner.get_word_aligns(d["src"], d["tgt"])[TYPE]
      #logging.info(f'Alignment: {d["counter"]}')
    except Exception as e:
      logging.error(f'Alignment error: {d["counter"]} {e}')
    
    processed.append(alignments)

  result = {
    "index": index,
    "data": processed
  }
  s2 = time.time()
  logging.info(f'Processing alignment {index} time: {s2-s1} seconds')

  if batch_save:
    save_alignments(pipeline, [result], index, batch_size)
    return None
  else:
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

  
  limit = config["params"]["limit"]

  if limit == 0 or len(sentences) < limit:
    limit = len(sentences)

  sentences = sentences[0:limit]

  processes = config["params"]["processes"]
  batch_size = config["params"]["batch_size"]
  batch_save = config["params"]["batch_save"]
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
      "gpu": gpu,
      "save": batch_save,
      "pipeline": args.pipeline,
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
    
    save_alignments(args.pipeline, sorted_result)

  t1 = time.time()

  logging.info(f'Total preprocessing time: {(t1 - t0):.2f} s')