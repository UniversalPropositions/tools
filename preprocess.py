import argparse
import time
import re

LINESEP = "\n"

def validate_alpha(text):
  for i in text:
    if i.isalpha():
      return True
  return False

def preprocess(s):
  s = s.replace("­", "") #\xad
  return re.sub('\s+',' ', s) #remove multiple spaces with one

def validate_tokens(text, min, max):
  tokens = text.split(" ")
  length = len(tokens)
  if length >= min and length <= max:
    return True
  return False

def validate(text, context):
  if not validate_alpha(text):
    return False, "Not alpha"
  if not validate_tokens(text, context["min_tokens"], context["max_tokens"]):
    return False, "Incorrect tokens length"
  if text in context["map"]:
    return False, "Duplicate" #we do not allow for duplicates both in source and target language
  else:
    context["map"][text] = {}
  return True, ""

def process_europarl(src, tgt, context):
  counter = 0
  for item in zip(src, tgt):
    s = preprocess(item[0])
    t = preprocess(item[1])
    counter += 1
    so, sm = validate(s, context)
    to, tm = validate(t, context)
    if so and to:
      context["europarl"]['src'].append(s)
      context["europarl"]['tgt'].append(t)
    else:
      context['log'].append(f'Skipping EUROPARL sentence {counter} / SRC: {s} / TGT: {t} / SRC MSG: {sm} / TGT MSG: {tm}')

def process_tatoeba(src, context):
  counter = 0
  for item in src:
    segments = item.split("\t")
    if len(segments) == 4:
      s = preprocess(segments[1])
      t = preprocess(segments[3])
      counter += 1
      so, sm = validate(s, context)
      to, tm = validate(t, context)
      if so and to:
        context["tatoeba"]['src'].append(s)
        context["tatoeba"]['tgt'].append(t)
      else:
        context['log'].append(f'Skipping TATOEBA sentence {counter} / SRC: {s} / TGT: {t} / SRC MSG: {sm} / TGT MSG: {tm}')

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Preprocessing')
  parser.add_argument('--europarl_src', type=str,
                      help='Input europarl parallel corpus source language EN')
  parser.add_argument('--europarl_tgt', type=str,
                      help='Input europarl parallel corpus target language')
  parser.add_argument('--tatoeba', type=str,
                      help='Input tatoeba parallel corpus')
  parser.add_argument('--output_src', type=str,
                      help='Output preprocessed parallel corpus source language EN')
  parser.add_argument('--output_tgt', type=str,
                      help='Output preprocessed parallel corpus target language')
  parser.add_argument('--output_log', type=str,
                      help='Output processing log')
  parser.add_argument('--min_tokens', type=int, default=2,
                      help='Minimal number of tokens')
  parser.add_argument('--max_tokens', type=int, default=100,
                      help='Maximal number of tokens')
  parser.add_argument('--max_sentences', type=int, default=0,
                      help='Maximal number of sentences')
  parser.add_argument('--split_ratio', type=float, default=0,
                      help='Split ratio between tatoeba and europarl, applies only if max_sentences is different than 0')

  args = parser.parse_args()

  t0 = time.time()

  context = {
    "europarl": {
      "src": [],
      "tgt": []
    },
    "tatoeba": {
      "src": [],
      "tgt": []
    },
    "log": [],
    "map": {},
    "min_tokens": args.min_tokens,
    "max_tokens": args.max_tokens
  }

  with open(args.europarl_src, "r", encoding="utf-8") as f:
    europarl_src = f.read().split(LINESEP)
  with open(args.europarl_tgt, "r", encoding="utf-8") as f:
    europarl_tgt = f.read().split(LINESEP)
  with open(args.tatoeba, "r", encoding="utf-8") as f:
    tatoeba = f.read().split(LINESEP)
  
  process_europarl(europarl_src, europarl_tgt, context)
  process_tatoeba(tatoeba, context)

  europarl_total = len(context["europarl"]["src"])
  tatoeba_total = len(context["tatoeba"]["src"])

  if args.max_sentences > 0:
    tatoeba_count = round(args.max_sentences * args.split_ratio)
    europarl_count = args.max_sentences - tatoeba_count
  else:
    europarl_count = europarl_total
    tatoeba_count = tatoeba_total

  if tatoeba_count > tatoeba_total:
    tatoeba_count = tatoeba_total
  
  if europarl_count > europarl_total:
    europarl_count = europarl_total

  print(f'Saving {tatoeba_count} tatoeba sentences and {europarl_count} europarl sentences.')

  with open(args.output_src, 'w', encoding='utf8') as f:
    f.write('\n'.join(context['europarl']['src'][0:europarl_count]))
    f.write("\n")
    f.write('\n'.join(context['tatoeba']['src'][0:tatoeba_count]))

  with open(args.output_tgt, 'w', encoding='utf8') as f:
    f.write('\n'.join(context['europarl']['tgt'][0:europarl_count]))
    f.write("\n")
    f.write('\n'.join(context['tatoeba']['tgt'][0:tatoeba_count]))

  with open(args.output_log, 'w', encoding='utf8') as f:
    f.write('\n'.join(context['log']))
  
  t1 = time.time()

  print(f'Total preprocessing time: {(t1 - t0):.2f} s')