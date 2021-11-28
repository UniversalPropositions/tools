import argparse
import time
import requests
import os
import zipfile
import logging
import impl.utils as utils
import glob

REPLACEMENTS = [
  {
    "src": "zh_cn",
    "tgt": "zh"
  }
]

logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./logs/download.log"),
    logging.StreamHandler()
  ]
)

def replacements(file):
  for r in REPLACEMENTS:
    file = file.replace(r['src'], r['tgt'])
  return file

def download_file(source, type, url):
  logging.info(f'Starting: {url}')
  dir = './data/source/' + source
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

  dir = './data/source/' + source + '/' + type
  for file in glob.glob(dir + "/*"):
    newfile = replacements(file)
    if newfile != file:
      os.rename(file, newfile)
      logging.info(f'Renaming {file} to {newfile}')

  logging.info(f'Completed: {url}, file size: {length} MB')

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Download')
  parser.add_argument('--source', type=str,
                      help='Language source')

  args = parser.parse_args()

  logging.info(f'Starting download: {args.source}')

  t0 = time.time()

  config = utils.read_config()

  if args.source not in config["sources"]:
    raise Exception("Source definition not available")

  downloads = config["sources"][args.source]
  for d in downloads["datasets"]:
    download_file(args.source, d, downloads["datasets"][d])

  t1 = time.time()

  logging.info(f'Total downloading time: {(t1 - t0):.2f} s')