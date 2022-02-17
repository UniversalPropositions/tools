"""
Word alignment outputs alignment on tokens
parser is on: words

Purpose of this script is two fold

- Obtain the token to word ids map from the inputs (Dependency parse and word alignment)
- Apply the computed map to token aligned sentences.
"""


import os
from megre_parse_srl import read_large_data


def generate_tok2wordmap(sen_parse, sen_tok):
    tokens = []
    for tok_line in sen_parse:
        if tok_line[0][0] != "#":
            tokens.append(tok_line[1])
    # TODO
    return

def write_tok2wordmap_to_file(t2w_map, filename):
    """
    write token to word map
    :param t2w_map: list of Dict
    :param filename: str
    :return:
    """
    f = open(filename, "w")
    for map_dict in t2w_map:
        f.write(" ".join([str(token)+"-"+str(parse) for token, parse in map_dict.items()]))
    f.close()

    return


def read_tok2wordmap_from_file(filename):
    """

    :param filename: string
    :return: list of dict
    """
    tok2word = []
    with open(filename, "r") as f:
        data = f.readlines()
    for sen_id, line in enumerate(data):
        maps = line.split(" ")
        tok2word_dict = {}
        for tok_id, m in enumerate(maps):
            if m[0] in tok2word_dict:
                print("Tokens to words have only one to many mappings. Other direction is not allowed")
                print("Problem appears in sentence id {} and tok id {}".format(sen_id, tok_id))
                break;
            else:
                tok2word_dict[m[0]] = m[1]
        tok2word.append(tok2word_dict)
    return tok2word


def apply_tok2wordmap(tok2word_map_t, tok2word_map_s, alignments):
    # TODO
    return



if __name__ == '__main__':
    import doctest
    doctest.testmod()

    parser_file = "/Users/ishan/git/Annotation-Projection/data/en-vi-exp/parsed/_en-vi-exp.vi.parsed.conllu"
    token_file = "/Users/ishan/git/Annotation-Projection/data/en-vi-exp/tokenized/_en-vi-exp.vi.tokenized.txt"

    with open(token_file, "r") as f_tok:
        tok_data = f_tok.readlines()

    for sen_id, sen in enumerate(read_large_data(parser_file)):
        tok2word = generate_tok2wordmap(sen, tok_data[sen_id])
        print("c")

