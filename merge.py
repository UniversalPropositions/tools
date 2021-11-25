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
    logging.FileHandler("./logs/merge.log"),
    logging.StreamHandler()
  ]
)

def merge_lang(pipeline, type, ext, lang):
  folder = "./data/" + pipeline + "/" + type
  try:
    mask = folder + "/tmp/" + pipeline + "." + lang + "*"
    name = folder + "/" + pipeline + "." + lang + "." + type + "." + ext
    files = glob.glob(mask)
    with open(name, 'w', encoding='utf8') as outfile:
      for file in files:
        with open(file, 'r', encoding='utf8') as f:
          for line in f:
            outfile.write(line)
        outfile.write("\n")
  except Exception as e:
    logging.error(e)

def merge(config, pipeline, type, ext):
  src = config["pipelines"][pipeline]["source"]
  src_lang = config["sources"][src]["src_lang"]
  tgt_lang = config["sources"][src]["tgt_lang"]
  merge_lang(pipeline, type, ext, src_lang)
  merge_lang(pipeline, type, ext, tgt_lang)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Merge')
  parser.add_argument('--pipeline', type=str)

  args = parser.parse_args()
 
  config = utils.read_config()

  if args.pipeline not in config["pipelines"]:
    raise Exception("Pipeline not available")

  s1 = time.time()

  logging.info(f'Processing {args.pipeline}')

  merge(config, args.pipeline, "tokenized","txt")
  merge(config, args.pipeline, "parsed", "conllu")

  s2 = time.time()
  logging.info(f'Total processing time: {s2-s1} seconds')