import stanza
import time
import argparse
import stanza
from multiprocessing import Pool
import torch
from stanza.utils.conll import CoNLL

LINESEP = "\n"

GPU = True
POOL_SIZE = 4
BATCH_SIZE = 10000
CUDA_DEVICES = 1

nlp = None

#torch.set_num_threads(1)

def process_batch(batch_data):
  s1 = time.time()
  global nlp
  index = batch_data["index"]
  lang = batch_data["lang"]
  dev = index % CUDA_DEVICES
  torch.cuda.set_device(dev)
  if not nlp:
    nlp = stanza.Pipeline(lang, processors='tokenize,pos,lemma,depparse', use_gpu=GPU, pos_batch_size=1000)
    print(f'Initializing NLP {index}')
  
  data = batch_data["data"]
  processed = nlp(data)
  result = {
    "index": index,
    "data": processed
  }
  s2 = time.time()
  print(f'Processing NLP {index} time: {s2-s1} seconds')
  return result

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Parsers evaluation')
  parser.add_argument('--input_file', type=str,
                      help='Input text file with sentences')
  parser.add_argument('--output_parsed_file', type=str,
                      help='Output parsed ConLLu file')
  parser.add_argument('--output_tokenized_file', type=str,
                      help='Output tokenized txt file')
  parser.add_argument('--lang', type=str,
                      help='Language: pl, de, es, fr, pt')

  args = parser.parse_args()

  stanza.download(args.lang)

  with open(args.input_file, "r", encoding="utf-8") as f:
    sentences = f.read().split(LINESEP)

  documents = [stanza.Document([], text=d) for d in sentences]
  #documents = sentences
  s1 = time.time()

  batches = []

  counter = 0
  for i in range(0, len(documents), BATCH_SIZE):
    counter += 1
    batch = counter % POOL_SIZE
    start = i
    end = start + BATCH_SIZE
    batches.append({
      "index": counter,
      "data": documents[start:end],
      "lang": args.lang
    })
    
  pool = Pool(POOL_SIZE)
  result = pool.map(process_batch, batches)

  sorted_result = sorted(result, key=lambda d: d['index']) 

  #tokenized sentences
  sentences = []
  for s in sorted_result:
    for d in s['data']:
      tokens = []
      #it should be always one sentence, we do not need to care about it
      for sent in d.sentences:
        for token in sent.tokens:
          tokens.append(token.text)
      sentence = " ".join(tokens)
      sentences.append(sentence)

  with open(args.output_tokenized_file, 'w', encoding='utf8') as f:
    f.write('\n'.join(sentences))

  counter = 0
  with open(args.output_parsed_file, 'w', encoding='utf8') as f:
    for s in sorted_result:
      for d in s['data']:
        counter += 1
        f.write("# sent_id = " + str(counter) + "\n")
        f.write("# text = " + sentences[counter - 1] + "\n")
        f.write(CoNLL.doc2conll_text(d))

  s2 = time.time()
  print(f'Total processing time: {s2-s1} seconds')