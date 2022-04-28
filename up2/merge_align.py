'''
Used only if params.save_batch is set to true. Allows to merge all the batch results 
from ./data/[pipeline]/align/tmp/ to a single file that contain all sentences stored 
in ./data/[pipeline]/align/ folder.
'''
import argparse
from up2.utils import read_config
import logging
import time
import glob
import os

os.makedirs("./logs", exist_ok=True)

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/merge_align.log"),
        logging.StreamHandler()
    ]
)


def merge(config: dict, pipeline: str):
    '''
    Merges alignment results stored in /tmp folder (for batch_save=true) into one file

    :param config: config/config.json file object
    :param pipeline: pipeline name from config/config.json file that is processed
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
        raise e

def merge_align(pipeline):
    config = read_config()

    if pipeline not in config["pipelines"]:
        msg = f'Pipeline for: {pipeline} not available'
        logging.error(msg)
        raise Exception(msg)

    s1 = time.time()

    logging.info(f'Processing {pipeline}')

    merge(config, pipeline)

    s2 = time.time()
    logging.info(f'Total processing time: {s2-s1} seconds')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Merge align')
    parser.add_argument('--pipeline', type=str)

    args = parser.parse_args()

    merge_align(args.pipeline)
