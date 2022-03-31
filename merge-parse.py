'''
Used only if params.save_batch is set to true. Allows to merge all the batch results 
from ./data/[pipeline]/tokenized/tmp/ and ./data/[pipeline]/parsed/tmp to single files 
that contain all sentences stored in ./data/[pipeline]/tokenized/ and 
./data/[pipeline]/parsed/ folders.
'''

import argparse
import impl.utils as utils
import logging
import time
import glob

logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./logs/mergeparse.log"),
    logging.StreamHandler()
  ]
)

def merge_lang(pipeline: str, type: str, ext: str, lang: str):
  '''
  Merges parse results for source or target language stored in /tmp folder (for batch_save=true) into one file

  :param pipeline: pipeline name from config.json file that is processed
  :param type: file type to be processed: parsed or tokenized
  :param ext: file extension to be processed
  :param lang: language to be processed
  '''
  folder = "./data/" + pipeline + "/" + type
  try:
    mask = folder + "/tmp/" + pipeline + "." + lang + "*"
    name = folder + "/" + pipeline + "." + lang + "." + type + "." + ext
    files = glob.glob(mask)
    files.sort()
    with open(name, 'w', encoding='utf8') as outfile:
      length = len(files) - 1
      for i, file in enumerate(files):
        with open(file, 'r', encoding='utf8') as f:
          for line in f:
            outfile.write(line)
        if i < length and type == "tokenized":
          outfile.write("\n")
  except Exception as e:
    logging.error(e)

def merge(config: dict, pipeline: str, type: str, ext: str):
  '''
  Merges parse results stored in /tmp folder (for batch_save=true) into one file

  :param config: config.json file content
  :param pipeline: pipeline name from config.json file that is processed
  :param type: file type to be processed: parsed or tokenized
  :param ext: file extension to be processed
  '''
  src = config["pipelines"][pipeline]["source"]
  src_lang = config["sources"][src]["src_lang"]
  tgt_lang = config["sources"][src]["tgt_lang"]
  merge_lang(pipeline, type, ext, src_lang)
  merge_lang(pipeline, type, ext, tgt_lang)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Merge parse')
  parser.add_argument('--pipeline', type=str)

  args = parser.parse_args()
 
  config = utils.read_config()

  if args.pipeline not in config["pipelines"]:
    raise Exception("Pipeline not available")

  s1 = time.time()

  logging.info(f'Processing {args.pipeline}')

  merge(config, args.pipeline, "tokenized", "txt")
  merge(config, args.pipeline, "parsed", "conllu")

  s2 = time.time()
  logging.info(f'Total processing time: {s2-s1} seconds')