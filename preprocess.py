import argparse
import time
import re
import impl.utils as utils
import logging
import glob
import os

LINESEP = "\n"

logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./logs/preprocess.log"),
    logging.StreamHandler()
  ]
)

def validate_alpha(text):
  for i in text:
    if i.isalpha():
      return True
  return False

def preprocess(s):
  s = s.replace("­", "") #\xad
  return re.sub('\s+',' ', s) #remove multiple spaces with one

def validate_tokens(text, min, max):
  global ml
  tokens = text.split(" ")
  length = len(tokens)  
  if length >= min and length <= max:
    return True
  return False

def validate(text, context):
  if not validate_alpha(text):
    return False, "Not alpha"
  params = context["config"]["params"]
  if not validate_tokens(text, params["min_tokens"], params["max_tokens"]):
    return False, "Incorrect tokens length"
  if text in context["map"]:
    return False, "Duplicate" #we do not allow for duplicates both in source and target language
  else:
    context["map"][text] = {}
  return True, ""

def get_data_from_file(folder, type, lang):
  path = folder + "/" + type + "/*."+lang
  files = glob.glob(path)
  if len(files) != 1:
    raise Exception(f'Problem with finding a file for {path}')
  with open(files[0], "r", encoding="utf-8") as f:
    return f.read().split(LINESEP)

def process(folder, type, src_lang, tgt_lang, context):
  data = context["data"]
  counter = 0
  src = get_data_from_file(folder, type, src_lang)
  tgt = get_data_from_file(folder, type, tgt_lang)
  for item in zip(src, tgt):
    s = preprocess(item[0])
    t = preprocess(item[1])
    counter += 1
    so, sm = validate(s, context)
    to, tm = validate(t, context)
    if so and to:
      data[type]['src'].append(s)
      data[type]['tgt'].append(t)
    else:
      context['log'].append(f'Skipping {type} sentence {counter} / SRC: {s} / TGT: {t} / SRC MSG: {sm} / TGT MSG: {tm}')

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Preprocess')
  parser.add_argument('--pipeline', type=str,
                      help='Language pipeline')

  args = parser.parse_args()

  logging.info(f'Starting preprocessing: {args.pipeline}')

  t0 = time.time()

  try:

    config = utils.read_config()

    args = parser.parse_args()

    t0 = time.time()

    if args.pipeline not in config["pipelines"]:
      raise Exception("Pipeline not available")

    context = {
      "data": {},
      "log": [],
      "map": {},
      "config": config
    }

    pipeline = config["pipelines"][args.pipeline]
    source = config["sources"][pipeline["source"]]
    datasets = source["datasets"]
    src_lang = source["src_lang"]
    tgt_lang = source["tgt_lang"]

    folder = "./data/source/" + pipeline["source"]

    for type in datasets:
      context["data"][type] = {
        "src": [],
        "tgt": []
      }
      process(folder, type, src_lang, tgt_lang, context)

    folder_br = "./data/" + args.pipeline +  "/bitext_raw"
    src_file = folder_br + "/" + args.pipeline + "." + src_lang + ".txt"
    tgt_file = folder_br + "/" + args.pipeline + "." + tgt_lang + ".txt"
    log_file = folder_br + "/preprocess.log"

    os.makedirs(folder_br, exist_ok = True)

    src_f = open(src_file, 'w', encoding='utf8')
    tgt_f = open(tgt_file, 'w', encoding='utf8')

    type_count = len(pipeline) - 1

    for i, type in enumerate(datasets):
      length = len(context["data"][type]["src"])

      sentences = pipeline["sentences"][type]

      if sentences == 0 or sentences > length:
        sentences = length

      logging.info(f'Saving {sentences} of {type} sentences.')

      src_f.write('\n'.join(context["data"][type]['src'][0:sentences]))
      tgt_f.write('\n'.join(context["data"][type]['tgt'][0:sentences]))
      if i < type_count:
        src_f.write("\n")
        tgt_f.write("\n")

    src_f.close()
    tgt_f.close()

    with open(log_file, 'w', encoding='utf8') as f:
      f.write('\n'.join(context['log']))
  
  except Exception as e:
    logging.error(e)
  
  t1 = time.time()

  logging.info(f'Total preprocessing time: {(t1 - t0):.2f} s')