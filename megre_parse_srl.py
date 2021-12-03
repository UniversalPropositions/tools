import os
import argparse
import impl.utils as utils

def read_large_data(filename):
    """
    To get one sentence at a time from a big file
    :param filename: path to the filename
    :return: Yield one sentence at a time
    """
    with open(filename) as f:
        data = f.readlines()

    all_sen = []
    sen = []
    for line in data:
        if line == "\n" or line == "---\n":
            if sen != []:
                yield sen
            sen = []
        else:
            sen.append(line.strip().split("\t"))
    if sen != []:
        yield sen




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Merge Parser with srl')
    parser.add_argument('--pipeline', type=str, default="en-fr-200k")

    args = parser.parse_args()
    config = utils.read_config()
    pipeline = config["pipelines"][args.pipeline]
    source = config["sources"][pipeline["source"]]
    src_lang = source["src_lang"]
    tgt_lang = source["tgt_lang"]

    folder = "./data/" + args.pipeline

    tokenized = folder + "/tokenized"

    parsed = folder + "/parsed"

    nnsrl = folder + "/labeled"

    if not os.path.exists(nnsrl):
        os.makedirs(nnsrl)

    parsed_file = os.path.join(parsed, "{}.{}.parsed.conllu".format(args.pipeline, src_lang))
    labeled_file = os.path.join(tokenized, "{}.{}.tokenized.txt.srl".format(args.pipeline, src_lang))

    # for sen_id, sen in enumerate(read_large_data(parsed_file)):
    #     print("\rsen no {}".format(sen_id), end="")
    # print("\n")
    # for sen_id, sen in enumerate(read_large_data(labeled_file)):
    #     print("\rsen no {}".format(sen_id), end="")
    # data = Reader(parsed_file, "conllu")
    i = 0
    for  sen_parse, sen_srl in zip(read_large_data(parsed_file), read_large_data(labeled_file)):
        print(sen_parse[1], sen_srl[0])
        if (i == 100) or (sen_parse[1] != sen_srl[0]):
            break
        i += 1

    print("haha")




