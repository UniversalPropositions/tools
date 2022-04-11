from matplotlib import pyplot as plt 
import numpy as np
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Sentence tokens histogram')
    parser.add_argument('--file', type=str,
                        help='Input file')

    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        europarl = f.read().split("\n")
    
    data = []
    for e in europarl:
        tokens = e.split(" ")
        data.append(len(tokens)) 

    fig = plt.figure(figsize =(10, 7))
    
    plt.hist(data, bins = range(0, 101, 10)) 
    
    plt.title("Tokens Histogram") 
    
    plt.show()