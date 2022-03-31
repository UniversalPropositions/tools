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
    logging.FileHandler("./logs/reversealign.log"),
    logging.StreamHandler()
  ]
)

def process(line):
  line = line.replace("\n", "")
  alignments = line.split(" ")
  new_alignments = []
  for alignment in alignments:
    segments = alignment.split("-")
    new_alignments.append(f'{segments[1]}-{segments[0]}')
  return " ".join(new_alignments) + "\n"

def reverse(config: dict, pipeline: str):
  '''
  Merges alignment results stored in /tmp folder (for batch_save=true) into one file

  :param config: config.json file content
  :param pipeline: pipeline name from config.json file that is processed
  '''

  folder = "./data/" + pipeline + "/aligned"

  infile = folder + "/_training.align"
  outfile = folder + "/__training.align"

  try:
    with open(outfile, 'w', encoding='utf8') as outf:
        with open(infile, 'r', encoding='utf8') as inf:
          for line in inf:
            line = process(line)
            outf.write(line)
  except Exception as e:
    logging.error(e)

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Reverse align')
  parser.add_argument('--pipeline', type=str)

  args = parser.parse_args()
 
  config = utils.read_config()

  if args.pipeline not in config["pipelines"]:
    raise Exception("Pipeline not available")

  s1 = time.time()

  logging.info(f'Processing {args.pipeline}')

  reverse(config, args.pipeline)

  s2 = time.time()
  logging.info(f'Total processing time: {s2-s1} seconds')