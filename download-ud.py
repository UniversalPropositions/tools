'''
Script downloads universal dependencies files based on configuration defined
in config/config.json file.
'''

import argparse
import time
import requests
import os
import zipfile
import logging
import impl.utils as utils
import glob
import re
from urllib.parse import urlparse


logging.basicConfig(
  format='%(asctime)s %(levelname)s %(message)s', 
  datefmt='%Y/%m/%d %H:%M:%S', 
  level=logging.INFO,
  handlers=[
    logging.FileHandler("./logs/download-ud.log"),
    logging.StreamHandler()
  ]
)

def download_file(source: str, url: str):
  '''
  Downloads the set of conllu files (dev, train, test) based on configuration in config.json file for specific universal-depencencies url
  
  :param source: config.json -> params.universal-dependencies - the name of definition that is used to download files
  :param url: destination URL used to download the set of conllu files (dev, train, test) configured in config.json
  '''
  logging.info(f'Starting: {url}')
  dir = './data/ud/' + source
  r = requests.get(url, allow_redirects=True)
  urlp = urlparse(url)
  if r.status_code == 404:
    print("URL does not exist")
  os.makedirs(dir, exist_ok = True)
  data = r.content
  html = data.decode("utf-8") 

  urls = re.findall("(?<=href=\").*?(?=.conllu)", html)

  length = 0

  for u in urls:
    uc = u + ".conllu"
    furl = urlp.scheme+"://"+urlp.netloc + uc
    furl = furl.replace("/blob/", "/raw/")
    r = requests.get(furl, allow_redirects=True)
    if r.status_code == 404:
      print("URL does not exist")
    data = r.content
    length += round(len(data) / 1024 / 1024)
    filename = os.path.basename(uc)
    path = dir + '/' + filename
    open(path, 'wb').write(data)

  logging.info(f'Completed: {url}, total files size (dev, train, test): {length} MB')

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
      description='Download')
  parser.add_argument('--ud', type=str,
                      help='Language universal-dependencies')

  args = parser.parse_args()

  logging.info(f'Starting download: {args.ud}')

  t0 = time.time()

  config = utils.read_config()

  if args.ud not in config["universal-dependencies"]:
    raise Exception("Universal dependencies definition not available")

  download_url = config["universal-dependencies"][args.ud]
  download_file(args.ud, download_url)

  t1 = time.time()

  logging.info(f'Total downloading time: {(t1 - t0):.2f} s')