'''
Script executes stanza tokenization on a given list of sentences for a given language 
and produces output CoNLL-U file and output tokenized file.
Input files are read from ./data/[pipeline]/bitext_raw/ folder.
Output files are stored in: ./data/[pipeline]/parsed/ and ./data/[pipeline]/tokenized/ folders.
'''

import multiprocessing
import stanza
import time
import argparse
import stanza
from multiprocessing import Pool
import torch
from stanza.utils.conll import CoNLL
import json
import logging
from utils import read_config, get_cuda_info, set_cuda_device
import os
from typing import List

if not os.path.exists("./logs/"):
    os.makedirs("./logs/")

logging.basicConfig(
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y/%m/%d %H:%M:%S',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("./logs/parse.log"),
        logging.StreamHandler()
    ]
)

LINESEP = "\n"

nlp = None


def doc2conll_text(doc: stanza.Document) -> str:
    '''
    Converts Stanza document to string that contains data in CoNLL-U format

    :param doc: stanza.Document to be converted
    :return: string with CoNLL-U data
    '''
    doc_conll = CoNLL.doc2conll(doc)
    for sentence in doc_conll:
        for i, line in enumerate(sentence):
            seg = line.split("\t")
            if len(seg[0].split("-")) == 2:
                del sentence[i]
    return "\n\n".join("\n".join(line for line in sentence)
                       for sentence in doc_conll) + "\n\n"


def check_if_result(pipeline: str, lang: str, index: int) -> bool:
    '''
    Checks if temporary result is available in the file system for a given pipeline, 
    language and batch index

    :param pipeline: processing pipeline from config.json file
    :param lang: source or target language identifier
    :param index: batch index to be checked
    :return: information if file is present or not
    '''
    folder_tokenized = "./data/" + pipeline + "/tokenized/tmp"
    s = ""
    if index:
        s = str(index).zfill(4) + "."
    file_tokenized = folder_tokenized + "/" + \
        pipeline + "." + lang + ".tokenized." + s + "txt"
    return os.path.isfile(file_tokenized)


def process_batch(batch_data: dict) -> dict:
    '''
    Processes single batch

    :param batch_data: dictionary containing all information required to process a given batch
    :return: dictionary with batch processing result, in case batch_save is set to true in 
            config.json None is returned and then merge-parse.py script must be used to merge partial
            results into one file
    '''
    s1 = time.time()
    global nlp

    index = batch_data["index"]
    processes = batch_data["processes"]
    logging.info(f'Starting batch {index}')
    batch_size = batch_data["batch_size"]
    batch_save = batch_data["save"]
    pipeline = batch_data["pipeline"]
    lang = batch_data["lang"]

    if batch_save:
        available = check_if_result(pipeline, lang, index)
        if available:
            logging.info(f'Skipping batch {index}')
            return None

    if not nlp:
        if processes > 1:
            current_process = int(
                multiprocessing.current_process().name.split('-')[1]) - 1
        else:
            current_process = 1
        gpu = batch_data["gpu"]
        if gpu:
            if torch.cuda.device_count() == 0:
                raise Exception("GPU device not found")
            device = current_process % torch.cuda.device_count()
            set_cuda_device(device)
        else:
            device = "cpu"
        lang = batch_data["lang"]
        # add tokenize_pretokenized=False in case we need to provide tokenized content
        nlp = stanza.Pipeline(lang, processors='tokenize,pos,lemma,depparse', use_gpu=gpu,
                              depparse_min_length_to_batch_separately=40, deepparse_batch_size=25)
        logging.info(
            f'Initializing NLP batch: {index}, process: {current_process}, device: {device}')

    data = batch_data["data"]
    #tokens = data.text.split(" ")
    processed = nlp(data)
    for p in processed:
        for s in p.sentences:
            for t in s.tokens:
                try:
                    if t.text is not None and t.text[-1] == " ":
                        t.text = t.text.strip()
                except Exception as e:
                    logging.error(e)
            for t in s.words:
                try:
                    if t.text is not None and t.text[-1] == " ":
                        t.text = t.text.strip()
                    if t.lemma is not None and t.lemma[-1] == " ":
                        t.lemma = t.lemma.strip()
                except Exception as e:
                    logging.error(e)

    result = {
        "index": index,
        "data": processed
    }
    s2 = time.time()
    logging.info(f'Processing batch {index} time: {s2-s1} seconds')

    if batch_save:
        save(pipeline, lang, [result], index, batch_size)
        return None
    else:
        return result


def process_language(config: dict, pipeline: str, lang: str, selected_sentences: List[int]):
    '''
    Prepares batches to be processed for a given language.

    :param config: dictionary with all configuration information
    :param pipeline: processed pipeline name from config.json file
    :param lang: processing language
    :selected_sentences: the list of sentences to be processed, in case of None all sentneces will be processed
    '''
    stanza.download(lang)

    input_file = "./data/" + pipeline + "/bitext_raw/" + pipeline + "." + lang + ".txt"

    with open(input_file, "r", encoding="utf-8") as f:
        sentences = f.read().split(LINESEP)

    sentences = list(filter(None, sentences))

    if selected_sentences:
        sentences = [sentences[i] for i in selected_sentences]

    limit = config["params"]["limit"]

    if limit == 0 or len(sentences) < limit:
        limit = len(sentences)

    documents = [stanza.Document([], text=d) for d in sentences[0:limit]]

    batches = []

    processes = config["params"]["processes"]
    batch_size = config["params"]["batch_size"]
    batch_save = config["params"]["batch_save"]
    gpu = config["params"]["gpu"]

    counter = 0
    for i in range(0, len(documents), batch_size):
        counter += 1
        start = i
        end = start + batch_size
        batches.append({
            "index": counter,
            "data": documents[start:end],
            "lang": lang,
            "gpu": gpu,
            "save": batch_save,
            "pipeline": pipeline,
            "batch_size": batch_size,
            "processes": processes
        })

    if processes > 1:
        pool = Pool(processes)
        result = pool.map(process_batch, batches)
    else:
        result = []
        for batch in batches:
            batch_result = process_batch(batch)
            result.append(batch_result)

    if not batch_save:

        sorted_result = sorted(result, key=lambda d: d['index'])

        save(pipeline, lang, sorted_result)


def save(pipeline: str, lang: str, sorted_result: dict, index: int = None, batch_size: int = None):
    '''
    Saves file with tokenized sentences and file with data in ConLL-U format

    :param pipeline: processed pipeline name from config.json file
    :param lang: processing language
    :param sorted_result: Stanza result to be saved into the files
    :index: batch number (applies only when config.json parameter batch_save=true)
    :batch_size: batch size (applies only when config.json parameter batch_save=true)
    '''
    asentences = []
    sentences = []
    tsentences = []
    for s in sorted_result:
        for d in s['data']:
            atokens = []
            # it should be always one sentence, we do not need to care about it
            for sent in d.sentences:
                for token in sent.tokens:
                    atokens.append(token.text)
            asentence = " ".join(atokens)
            tokens = []
            for sent in d.sentences:
                for word in sent.words:
                    tokens.append(word.text)
            sentence = " ".join(tokens)
            tsentence = "|||".join(tokens)

            asentences.append(asentence)
            sentences.append(sentence)
            tsentences.append(tsentence)

    s = ""
    if index:
        s = "/tmp"
    folder_parsed = "./data/" + pipeline + "/parsed" + s
    folder_tokenized = "./data/" + pipeline + "/tokenized" + s
    os.makedirs(folder_parsed, exist_ok=True)
    os.makedirs(folder_tokenized, exist_ok=True)

    s = ""
    if index:
        s = str(index).zfill(4) + "."

    file_parsed = folder_parsed + "/" + pipeline + \
        "." + lang + ".parsed." + s + "conllu"
    file_tokenized = folder_tokenized + "/" + \
        pipeline + "." + lang + ".tokenized." + s + "txt"

    with open(file_tokenized, 'w', encoding='utf8') as f:
        f.write('\n'.join(tsentences))

    counter = 0
    with open(file_parsed, 'w', encoding='utf8') as f:
        for s in sorted_result:
            for d in s['data']:
                counter += 1
                if index and batch_size:
                    sent = (index - 1) * batch_size + counter
                else:
                    sent = counter
                f.write("# sent_id = " + str(sent) + "\n")
                if sentences[counter - 1] != asentences[counter - 1]:
                    f.write("# actual text = " +
                            asentences[counter - 1] + "\n")
                f.write("# text = " + sentences[counter - 1] + "\n")
                conllu = doc2conll_text(d)
                f.write(conllu)

def parse(pipeline, lang):
    config = read_config()

    if pipeline not in config["pipelines"]:
        msg = f'Pipeline for: {pipeline} not available'
        logging.error(msg)
        raise Exception(msg)

    selected_sentences = []
    try:
        with open("./data/" + pipeline + "/ids.txt", "r", encoding="utf-8") as f:
            list = f.read().split(LINESEP)
            for l in list:
                selected_sentences.append(int(l) - 1)
    except Exception:
        selected_sentences = None

    cuda = get_cuda_info()

    logging.info("Cuda: " + json.dumps(cuda))

    s1 = time.time()

    logging.info(f'Processing {lang}')

    process_language(config, pipeline, lang, selected_sentences)

    s2 = time.time()
    logging.info(f'Total processing time: {s2-s1} seconds')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Parsers evaluation')
    parser.add_argument('--pipeline', type=str)
    parser.add_argument('--lang', type=str)

    args = parser.parse_args()

    parse(args.pipeline, args.lang)
