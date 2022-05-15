'''
Script downloads selected parallel corpus based on configuration defined
in config/config.json file.
'''
import argparse
import time
import requests
import os
import zipfile
import logging
from utils import read_config
import glob

REPLACEMENTS = [
    {
        "src": "zh_cn",
        "tgt": "zh"
    }
]

if not os.path.exists("./logs/"):
    os.makedirs("./logs/")

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/download.log"),
        logging.StreamHandler()
    ]
)


def replacements(file: str) -> str:
    '''
    Updates file names for selected languages based on REPLACEMENTS constant

    :param file: file name to be updated
    :return: updated file name
    '''
    for r in REPLACEMENTS:
        file = file.replace(r['src'], r['tgt'])
    return file


def download_file(source: str, type: str, url: str):
    '''
    Downloads the set of files based on configuration in config/config.json file for specific dataset and url

    :param source: config.json -> sources - the name of source definition that is used to download files
    :param type: one of: europarl, tatoeba, subtitles
    :param url: destination URL used to download a file configured in config/config.json
    '''
    logging.info(f'Starting: {url}')
    dir = './data/source/' + source
    os.makedirs(dir, exist_ok=True)
    segments = url.split("/")
    file = segments[len(segments) - 1]
    path = dir + '/' + file
    if "http" not in url:
        with open(url, "rb") as f:
            data = f.read()
    else:
        r = requests.get(url, allow_redirects=True)
        if r.status_code == 404:
            msg = f'URL: {url} does not exist'
            logging.error(msg)
            raise Exception(msg)
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

def download(source):
    logging.info(f'Starting download: {source}')

    t0 = time.time()

    config = read_config()

    if source not in config["sources"]:
        msg = f'Sources definition for: {source} not available'
        logging.error(msg)
        raise Exception(msg)

    downloads = config["sources"][source]
    for d in downloads["datasets"]:
        download_file(source, d, downloads["datasets"][d])

    t1 = time.time()

    logging.info(f'Total downloading time: {(t1 - t0):.2f} s')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Download')
    parser.add_argument('--source', type=str,
                        help='Language pair from config/config.json -> sources for example: en-de')

    args = parser.parse_args()

    download(args.source)
