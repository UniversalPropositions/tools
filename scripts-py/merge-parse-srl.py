import os
import argparse
from utils import read_config

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
    config = read_config()
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

    parsed_file = os.path.join(parsed, "_{}.{}.parsed.conllu".format(args.pipeline, src_lang))
    srl_file = os.path.join(tokenized, "_{}.{}.tokenized.txt.srl".format(args.pipeline, src_lang))
    labeled_file = os.path.join(nnsrl, "_{}.{}.labeled.nn.conllu".format(args.pipeline, src_lang))
    f_out = open(labeled_file, "w")
    # for sen_id, sen in enumerate(read_large_data(parsed_file)):
    #     print("\rsen no {}".format(sen_id), end="")
    # print("\n")
    # for sen_id, sen in enumerate(read_large_data(labeled_file)):
    #     print("\rsen no {}".format(sen_id), end="")
    # data = Reader(parsed_file, "conllu")
    i = 0
    for  sen_parse, sen_srl in zip(read_large_data(parsed_file), read_large_data(srl_file)):
        # print(sen_parse[1], sen_srl[0])
        parse_srl = []
        parse_sen = []
        srl_sen = []
        if (sen_parse[1] != sen_srl[0]):
            break
        else:
            for parse_s in sen_parse:
                if parse_s[0][0:2] == "# ":
                    parse_srl.append(parse_s)
                else:
                    parse_sen.append(parse_s)
            for srl_s in sen_srl:
                if "span_srl" in srl_s[0]:
                    parse_srl.append(srl_s)
                elif srl_s[0][0:2] == "# ":
                    continue
                else:
                    srl_sen.append(srl_s)
            if len(parse_sen) != len(srl_sen):
                print(sen_parse[1])
                continue
            parse_sen = list(map(list, zip(*parse_sen)))[:-2]
            srl_sen = list(map(list, zip(*srl_sen)))[1:]
            parse_sen.extend(srl_sen)
            parse_sen = list(map(list, zip(*parse_sen)))
            parse_srl.extend(parse_sen)
            for tok_line in parse_srl:
                f_out.write("\t".join(tok_line)+"\n")
            f_out.write("\n")

        i += 1
    f_out.close()
    print("haha")




