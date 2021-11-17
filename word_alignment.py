import argparse
from conllu import parse_incr
import time
from simalign import SentenceAligner
from multiprocessing import Pool
import torch

LINESEP = "\n"
TYPE = 'itermax'
aligner = None

def save_alignments(file, batches):
  sentences = []
  for b in batches:
    for d in b["data"]:
      sentence = ' '.join([str(x[0]) + '-' + str(x[1]) for x in d])
      sentences.append(sentence)
  
  with open(file, 'w', encoding='utf8') as f:
    f.write('\n'.join(sentences))

def process_batch(batch_data):
  s1 = time.time()
  global aligner
  index = batch_data["index"]
  lang = batch_data["lang"]
  cuda_devices = batch_data["cuda_devices"]
  gpu = batch_data["gpu"]
  dev = index % cuda_devices
  torch.cuda.set_device(dev)
  if not aligner:
    aligner = SentenceAligner(model="bert", token_type="word", matching_methods="mai", device='cuda')
    print(f'Initializing aligner {index}')
  
  data = batch_data["data"]
  processed = []
  
  s1 = time.time()

  for d in data:
    alignments = aligner.get_word_aligns(d["src"], d["tgt"])[TYPE]
    print(f'Alignment: {d["counter"]}')
    processed.append(alignments)
    

  result = {
    "index": index,
    "data": processed
  }
  s2 = time.time()
  print(f'Processing alignment {index} time: {s2-s1} seconds')
  
  return result

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Word alignment evaluation')
  parser.add_argument('--input_tokenized_source', type=str,
                      help='Input file with tokenized source sentences')
  parser.add_argument('--input_tokenized_target', type=str,
                      help='Input file with tokenized target sentences')
  parser.add_argument('--output_file', type=str,
                      help='Output file with alignments')
  parser.add_argument('--gpu', type=bool, default=True,
                      help='True/False - if GPU should be used')
  parser.add_argument('--pool_size', type=int, default=4,
                      help='Number of parallel processes')
  parser.add_argument('--batch_size', type=int, default=10000,
                      help='Number of samples to be processed in one iteration within single process')
  parser.add_argument('--cuda_devices', type=int, default=1,
                      help='Number of GPUs that should be used')
  parser.add_argument('--lang', type=str,
                  help='Target language'),

  args = parser.parse_args()

  with open(args.input_tokenized_source, "r", encoding="utf-8") as f:
    source_data = f.read().split(LINESEP)

  with open(args.input_tokenized_target, "r", encoding="utf-8") as f:
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

  sentences = sentences[0:20]

  counter = 0
  batches = []
  for i in range(0, len(sentences), args.batch_size):
    counter += 1
    batch = counter % args.pool_size
    start = i
    end = start + args.batch_size
    batches.append({
      "index": counter,
      "data": sentences[start:end],
      "lang": args.lang,
      "gpu": args.gpu,
      "cuda_devices": args.cuda_devices
    })
    
  pool = Pool(args.pool_size)
  result = pool.map(process_batch, batches)

  sorted_result = sorted(result, key=lambda d: d['index']) 
  
  save_alignments(args.output_file, sorted_result)

  t1 = time.time()

  print(f'Total preprocessing time: {(t1 - t0):.2f} s')