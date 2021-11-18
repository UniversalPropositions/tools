import stanza
import time
import argparse
import stanza
from multiprocessing import Pool
import torch
from stanza.utils.conll import CoNLL

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
  lang = batch_data["lang"]
  cuda_devices = batch_data["cuda_devices"]
  gpu = batch_data["gpu"]
  if gpu:
    dev = index % cuda_devices
    torch.cuda.set_device(dev)
  if not nlp:
    nlp = stanza.Pipeline(lang, processors='tokenize,pos,lemma,depparse', use_gpu=gpu, pos_batch_size=1000)
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
  parser.add_argument('--gpu', type=bool, default=True,
                      help='True/False - if GPU should be used')
  parser.add_argument('--pool_size', type=int, default=4,
                      help='Number of parallel processes')
  parser.add_argument('--batch_size', type=int, default=10000,
                      help='Number of samples to be processed in one iteration within single process')
  parser.add_argument('--cuda_devices', type=int, default=1,
                      help='Number of GPUs that should be used')
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
  for i in range(0, len(documents), args.batch_size):
    counter += 1
    batch = counter % args.pool_size
    start = i
    end = start + args.batch_size
    batches.append({
      "index": counter,
      "data": documents[start:end],
      "lang": args.lang,
      "gpu": args.gpu,
      "cuda_devices": args.cuda_devices
    })
    
  pool = Pool(args.pool_size)
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

  with open(args.output_tokenized_file, 'w', encoding='utf8') as f:
    f.write('\n'.join(sentences))

  counter = 0
  with open(args.output_parsed_file, 'w', encoding='utf8') as f:
    for s in sorted_result:
      for d in s['data']:
        counter += 1
        f.write("# sent_id = " + str(counter) + "\n")
        if sentences[counter - 1] != asentences[counter - 1]:
          f.write("# actual text = " + asentences[counter - 1] + "\n")
        f.write("# text = " + sentences[counter - 1] + "\n")
        conllu = doc2conll_text(d)
        f.write(conllu)

  s2 = time.time()
  print(f'Total processing time: {s2-s1} seconds')