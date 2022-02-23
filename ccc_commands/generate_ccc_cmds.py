import pandas as pd
import json

def full_pipeline_per_pair(pair):
    sl, tl = pair.split("-")

    get_data = "jbsub -mem 64g -cores 1+1 -out logs/dnld-{} -name dnld-{}  'python download.py --source={}'".format(tl,
                                                                                                                    tl,
                                                                                                                    pair)
    pre_data = "jbsub -mem 64g -cores 1+1 -out logs/pre-{} -name pre-{}  'python preprocess.py --pipeline={}'".format(
        tl, tl, pair)
    parse_en_data = "jbsub -mem 64g -cores 1+1 -out logs/par-{} -name par-{} -require v100 'python parse.py --pipeline={} --lang={}'".format(
        sl + tl + sl, sl + tl + sl, pair, sl)
    parse_tl_data = "jbsub -mem 64g -cores 1+1 -out logs/par-{} -name par-{} -require v100 'python parse.py --pipeline={} --lang={}'".format(
        sl + tl + tl, sl + tl + tl, pair, tl)
    merge_parse = "jbsub -mem 64g -cores 1+1 -out logs/parjoin-{} -name parjoin-{} 'python merge-parse.py --pipeline={}'".format(
        sl + tl + tl, sl + tl + tl, pair)
    aligner = "jbsub -mem 64g -cores 1+1 -out logs/wd-{} -name wd-{} -require v100 'python wordalignment.py --pipeline={}'".format(
        sl + tl, sl + tl, pair)
    merge_aligner = "jbsub -mem 64g -cores 1+1 -out logs/Mwd-{} -name Mwd-{} 'python merge-align.py --pipeline={}'".format(
        sl + tl, sl + tl, pair)
    post_data = "jbsub -mem 64g -cores 1+1 -out logs/post-{} -name post-{} 'python postprocess.py --pipeline={}'".format(
        sl + tl, sl + tl, pair)

    print("\n".join([get_data, pre_data, parse_en_data, parse_tl_data, merge_parse, aligner, merge_aligner, post_data]))
    print("\n")


def full_pipeline_all_pair(pairs):
    get_data = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        get_data += "jbsub -mem 64g -cores 1+1 -out logs/dnld-{} -name dnld-{}  'python download.py --source={}'\n".format(tl,
                                                                                                                        tl,
                                                                                                                        pair)
    print(get_data)

    pre_data = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        pre_data += "jbsub -mem 64g -cores 1+1 -out logs/pre-{} -name pre-{}  'python preprocess.py --pipeline={}'\n".format(
        tl, tl, pair)

    print(pre_data)

    parse_en_data = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        parse_en_data += "jbsub -mem 64g -cores 1+1 -out logs/par-{} -name par-{} -require v100 'python parse.py --pipeline={} --lang={}'\n".format(
        sl + tl + tl, sl + tl + tl, pair, tl)

    print(parse_en_data)


    parse_tl_data = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        parse_tl_data += "jbsub -mem 64g -cores 1+1 -out logs/par-{} -name par-{} -require v100 'python parse.py --pipeline={} --lang={}'\n".format(
            sl + tl + tl, sl + tl + tl, pair, tl)

    print(parse_tl_data)


    merge_parse = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        merge_parse += "jbsub -mem 64g -cores 1+1 -out logs/parjoin-{} -name parjoin-{} 'python merge-parse.py --pipeline={}'\n".format(
            sl + tl + tl, sl + tl + tl, pair)

    print(merge_parse)


    aligner = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        aligner += "jbsub -mem 64g -cores 1+1 -out logs/wd-{} -name wd-{} -require v100 'python wordalignment.py --pipeline={}'\n".format(
            sl + tl, sl + tl, pair)

    print(aligner)


    merge_aligner = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        merge_aligner += "jbsub -mem 64g -cores 1+1 -out logs/Mwd-{} -name Mwd-{} 'python merge-align.py --pipeline={}'\n".format(
            sl + tl, sl + tl, pair)


    print(merge_aligner)


    post_data = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        post_data += "jbsub -mem 64g -cores 1+1 -out logs/post-{} -name post-{} 'python postprocess.py --pipeline={}'\n".format(
            sl + tl, sl + tl, pair)

    print(post_data)


def full_pipeline_all_pair_sample(pairs, sample):
    get_data = ""
    for pair in pairs:
        sl, tl = pair.split("-")
        get_data += "jbsub -mem 64g -cores 1+1 -out logs/dnld-{} -name dnld-{}  'python download.py --source={}'\n".format(tl,
                                                                                                                        tl,
                                                                                                                        pair)
    print(get_data)

    pre_data = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        pre_data += "jbsub -mem 64g -cores 1+1 -out logs/pre-{} -name pre-{}  'python preprocess.py --pipeline={}'\n".format(
        tl+"-"+str(sample), tl+"-"+str(sample), pair+"-"+str(sample))

    print(pre_data)

    parse_en_data = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        parse_en_data += "jbsub -mem 64g -cores 1+1 -out logs/par-{} -name par-{} -require v100 'python parse.py --pipeline={} --lang={}'\n".format(
        sl + tl + tl+"-"+str(sample), sl + tl + tl+"-"+str(sample), pair+"-"+str(sample), tl)

    print(parse_en_data)


    parse_tl_data = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        parse_tl_data += "jbsub -mem 64g -cores 1+1 -out logs/par-{} -name par-{} -require v100 'python parse.py --pipeline={} --lang={}'\n".format(
            sl + tl + tl+"-"+str(sample), sl + tl + tl+"-"+str(sample), pair+"-"+str(sample), tl)

    print(parse_tl_data)


    merge_parse = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        merge_parse += "jbsub -mem 64g -cores 1+1 -out logs/parjoin-{} -name parjoin-{} 'python merge-parse.py --pipeline={}'\n".format(
            sl + tl + tl+"-"+str(sample), sl + tl + tl+"-"+str(sample), pair+"-"+str(sample))

    print(merge_parse)


    aligner = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        aligner += "jbsub -mem 64g -cores 1+1 -out logs/wd-{} -name wd-{} -require v100 'python wordalignment.py --pipeline={}'\n".format(
            sl + tl+"-"+str(sample), sl + tl+"-"+str(sample), pair+"-"+str(sample))

    print(aligner)


    merge_aligner = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        merge_aligner += "jbsub -mem 64g -cores 1+1 -out logs/Mwd-{} -name Mwd-{} 'python merge-align.py --pipeline={}'\n".format(
            sl + tl+"-"+str(sample), sl + tl+"-"+str(sample), pair+"-"+str(sample))


    print(merge_aligner)


    post_data = ""
    for pair in pairs:
        sl, tl = pair.split("-")

        post_data += "jbsub -mem 64g -cores 1+1 -out logs/post-{} -name post-{} 'python postprocess.py --pipeline={}'\n".format(
            sl + tl+"-"+str(sample), sl + tl+"-"+str(sample), pair+"-"+str(sample))

    print(post_data)


def generate_config(pairs, df, subset=100):

    data = {"params": {}, "pipelines": {}, "sources": {}}

    # data["params"] = {}
    # data["params"]["min_tokens"] = 5,
    # data["params"]["max_tokens"] = 80,
    # data["params"]["gpu"] = True,
    # data["params"]["processes"] = 1,
    # data["params"]["batch_size"] = 10000,
    # data["params"]["batch_save"] = True,
    # data["params"]["limit"] = 0,
    # data["params"]["excluded_tokens_validation"] = ["zh"]

    for pair in pairs:
        sources = 0
        sl, tl = pair.split("-")
        data["sources"][pair] = {}
        data["sources"][pair]["src_lang"] = sl
        data["sources"][pair]["tgt_lang"] = tl
        data["sources"][pair]["datasets"] = {}
        if tl in df["europarl"].values:
            data["sources"][pair]["datasets"] ["europarl"] = "https://object.pouta.csc.fi/OPUS-Europarl/v8/moses/{}.txt.zip".format(pair)
        elif tl in df["opensubtitles"].values:
            data["sources"][pair]["datasets"] ["subtitles"] = "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/moses/{}.txt.zip".format(pair)
        if tl in df["tatoeba"].values:
            data["sources"][pair]["datasets"][
                "tatoeba"] = "https://object.pouta.csc.fi/OPUS-Tatoeba/v2021-07-22/moses/{}.txt.zip".format(pair)
        if tl == "zh":
            data["sources"][pair]["datasets"][
                "subtitles"] = "https://object.pouta.csc.fi/OPUS-OpenSubtitles/v2018/moses/{}.txt.zip".format(pair+"_cn")

        data["pipelines"][pair] = {}
        data["pipelines"][pair]["source"] = pair
        data["pipelines"][pair]["sentences"] = {}
        if tl in df["europarl"].values:
            data["pipelines"][pair]["sentences"]["europarl"] = 0
            sources += 1
        elif tl in df["opensubtitles"].values:
            data["pipelines"][pair]["sentences"]["subtitles"] = 0
            sources += 1
        if tl in df["tatoeba"].values:
            data["pipelines"][pair]["sentences"]["tatoeba"] = 0
            sources += 1

        if tl == "zh":
            data["pipelines"][pair]["sentences"]["subtitles"] = 0
            sources += 1

        if subset !=0:
            frac = int(subset/sources)
            pair = pair+"-"+str(subset)
            data["pipelines"][pair] = {}
            data["pipelines"][pair]["source"] = pair
            data["pipelines"][pair]["sentences"] = {}
            if tl in df["europarl"].values:
                data["pipelines"][pair]["sentences"]["europarl"] = frac
            elif tl in df["opensubtitles"].values:
                data["pipelines"][pair]["sentences"]["subtitles"] = frac
            if tl in df["tatoeba"].values:
                data["pipelines"][pair]["sentences"]["tatoeba"] = frac

            if tl == "zh":
                data["pipelines"][pair]["sentences"]["subtitles"] = frac

    return data


if __name__ == "__main__":

    with open("../sr-tl.txt", "r") as f:
        pairs = f.readlines()
    pairs = [x.strip() for x in pairs]
    pair = "en-fr"
    for pair in pairs:
        full_pipeline_per_pair(pair)

    full_pipeline_all_pair(pairs)

    xl_file = pd.ExcelFile("/Users/ishan/git/up2/language_selection/lng_data.xlsx")
    dfs = {sheet_name: xl_file.parse(sheet_name)
           for sheet_name in xl_file.sheet_names}

    config = generate_config(pairs, dfs["Common_languages"])

    with open("config_new.json", "w") as file:

        app_json = json.dump(config, file, indent=4)
    # print(app_json)
    full_pipeline_all_pair_sample(pairs, 100)





