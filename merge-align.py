'''
Used only if params.save_batch is set to true. Allows to merge all the batch results 
from ./data/[pipeline]/align/tmp/ to a single file that contain all sentences stored 
in ./data/[pipeline]/align/ folder.
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
    logging.FileHandler("./logs/mergealign.log"),
    logging.StreamHandler()
  ]
)

def merge(config: dict, pipeline: str):
  '''
  Merges alignment results stored in /tmp folder (for batch_save=true) into one file

  :param config: config.json file content
  :param pipeline: pipeline name from config.json file that is processed
  '''
  folder = "./data/" + pipeline + "/aligned"
  try:
    mask = folder + "/tmp/training.*.align"
    name = folder + "/training.align"
    files = glob.glob(mask)
    files.sort()
    with open(name, 'w', encoding='utf8') as outfile:
      length = len(files) - 1
      for i, file in enumerate(files):
        with open(file, 'r', encoding='utf8') as f:
          for line in f:
            outfile.write(line)
        if i < length:
          outfile.write("\n")
  except Exception as e:
    logging.error(e)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Merge align')
  parser.add_argument('--pipeline', type=str)

  args = parser.parse_args()
 
  config = utils.read_config()

  if args.pipeline not in config["pipelines"]:
    raise Exception("Pipeline not available")

  s1 = time.time()

  logging.info(f'Processing {args.pipeline}')

  merge(config, args.pipeline)

  s2 = time.time()
  logging.info(f'Total processing time: {s2-s1} seconds')