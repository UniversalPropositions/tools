import argparse
import time
import requests
import os
import zipfile
import logging
import impl.utils as utils

logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./data/logs/download.log"),
    logging.StreamHandler()
  ]
)

def download_file(pipeline, type, url):
  logging.info(f'Starting: {url}')
  dir = './data/source/' + pipeline
  segments = url.split("/")
  file = segments[len(segments) - 1]
  path = dir + '/' + file
  r = requests.get(url, allow_redirects=True)
  os.makedirs(dir, exist_ok = True)
  data = r.content
  length = round(len(data) / 1024 / 1024)
  open(path, 'wb').write(data)
  with zipfile.ZipFile(path, "r") as zip:
    zip.extractall(dir + "/" + type)
  os.remove(path)
  logging.info(f'Completed: {url}, file size: {length} MB')

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Download')
  parser.add_argument('--pipeline', type=str,
                      help='Language pipeline')

  args = parser.parse_args()

  logging.info(f'Starting download: {args.pipeline}')

  t0 = time.time()

  config = utils.read_config()

  if args.pipeline not in config["pipelines"]:
    raise Exception("Pipeline not available")

  downloads = config["pipelines"][args.pipeline]
  for d in downloads:
    download_file(args.pipeline, d, downloads[d])

  t1 = time.time()

  logging.info(f'Total downloading time: {(t1 - t0):.2f} s')