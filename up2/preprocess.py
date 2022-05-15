'''
Script prepares parallel corpus based on datasets in moses format configured in 
config/config.json file.
Processing results are stored in ./data/[pipeline]/bitext_raw/ folder.
'''

import argparse
import time
import re
from utils import read_config
import logging
import glob
import os
from typing import Tuple, List

LINESEP = "\n"

if not os.path.exists("./logs/"):
    os.makedirs("./logs/")

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/preprocess.log"),
        logging.StreamHandler()
    ]
)


def validate_alpha(text: str) -> bool:
    '''
    Performs three validations checking if there are some incorrect characters in a sentence
    that can cause later problem during processing. Our goal is to remove such sentences from processing.
    Verifications:
    - check for "\\x" and "\\u" characters
    - check for "�" character
    - check if there is at least one alpha character in a given sentence

    :param text: text to be validated
    :return: validation result
    '''
    # check for \\x and \\u characters
    for tok in text:
        r = repr(tok)
        if "\\x" in r or "\\u" in r:
            return False
    # check for "�" character
    if "�" in text:
        return False
    # check if there is at least one alpha character in a given sentence
    for tok in text:
        if tok.isalpha():
            return True
    return False


def preprocess_sentence(sentence: str) -> str:
    '''
    Replaces all multiple spaces in a given sentence with one space

    :param sentence: sentence to be fixed
    :return: fixed sentence
    '''
    result = re.sub('\s+', ' ', sentence)
    return result


def validate_tokens(text: str, min: int, max: int) -> bool:
    '''
    Validates tokens length. We select sentences for further processing with tokens length between 
    config/params/min_tokens and config/params/max_tokens. 

    :param text: text to be validated
    :param min: min acceptable tokens length
    :param max: max acceptable tokens length
    :return: token validation result
    '''
    tokens = text.split(" ")
    length = len(tokens)
    if length >= min and length <= max:
        return True
    return False


def validate(text: str, context: dict, lang: str) -> Tuple[bool, str]:
    '''
    Main validation function that calls:
    - validate_alpha
    - validate tokens (excluding some languages: ZH where we cannot apply filtering based on tokens length)
    - exclude duplicated sentences from processed dataset - there is a common map for source and target language.

    :param text: text to be validated
    :param context: context object with configuration
    :param lang: language for which validation will be performed
    :return: validation result
    :return: validation error message
    '''
    if not validate_alpha(text):
        return False, "Alpha validation failed"
    params = context["config"]["params"]
    if lang not in params["excluded_tokens_validation"]:
        if not validate_tokens(text, params["min_tokens"], params["max_tokens"]):
            return False, "Incorrect tokens length"
    if text in context["map"]:
        return False, "Duplicate sentence"
    else:
        context["map"][text] = {}
    return True, ""


def get_data_from_file(folder: str, type: str, lang: str) -> List[str]:
    '''
    Reads the content of source file with raw parallel corpus for a given language

    :param folder: folder that contains a file to be read
    :param type: type of source file: europarl, tatoeba, subtitles
    :param lang: we read only a file for src or tgt language
    :return: list of strings with sentences
    '''
    path = folder + "/" + type + "/*."+lang
    files = glob.glob(path)
    if len(files) != 1:
        raise Exception(f'Problem with finding a file for {path}')
    with open(files[0], "r", encoding="utf-8") as f:
        return f.read().split(LINESEP)


def process(folder: str, type: str, src_lang: str, tgt_lang: str, context: dict):
    '''
    The main processing function

    :param folder: folder that contains a file to be read
    :param type: type of source file: europarl, tatoeba, subtitles
    :param src_lang: source language for parallel corpus
    :param tgt_lang: target language for parallel corpus
    :param context: context with processing parameters
    '''
    data = context["data"]
    counter = 0
    src = get_data_from_file(folder, type, src_lang)
    tgt = get_data_from_file(folder, type, tgt_lang)
    for item in zip(src, tgt):
        s = preprocess_sentence(item[0])
        t = preprocess_sentence(item[1])
        counter += 1
        if counter % 1000 == 0:
            logging.info(f'{counter}')
        so, sm = validate(s, context, src_lang)
        to, tm = validate(t, context, tgt_lang)
        if so and to:
            data[type]['src'].append(s)
            data[type]['tgt'].append(t)
        else:
            context['log'].append(
                f'Skipping {type} sentence {counter} / SRC: {s} / TGT: {t} / SRC MSG: {sm} / TGT MSG: {tm}')


def preprocess(arg_pipeline):
    logging.info(f'Starting preprocessing: {arg_pipeline}')

    t0 = time.time()

    try:

        config = read_config()

        t0 = time.time()

        if arg_pipeline not in config["pipelines"]:
            raise Exception("Pipeline not available")

        context = {
            "data": {},
            "log": [],
            "map": {},
            "config": config
        }

        pipeline = config["pipelines"][arg_pipeline]
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

        folder_br = "./data/" + arg_pipeline + "/bitext_raw"
        src_file = folder_br + "/" + arg_pipeline + "." + src_lang + ".txt"
        tgt_file = folder_br + "/" + arg_pipeline + "." + tgt_lang + ".txt"
        log_file = folder_br + "/preprocess.log"

        os.makedirs(folder_br, exist_ok=True)

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
        raise e

    t1 = time.time()

    logging.info(f'Total preprocessing time: {(t1 - t0):.2f} s')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Preprocess')
    parser.add_argument('--pipeline', type=str,
                        help='Language pipeline')

    args = parser.parse_args()

    preprocess(args.pipeline)