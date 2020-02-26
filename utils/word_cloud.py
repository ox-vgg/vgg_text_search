__author__      = 'Ernesto Coto'
__copyright__   = 'February 2020'

import sys
import os
from collections import Counter
import json
import math
import csv

def print_usage():
    print ("Application used to generate a text file with a list of the most frequent words in the images index")
    print ("Usage:")
    print ("python %s results_list results_dir out_file" % sys.argv[0])

if __name__ == "__main__":
    """
        Application used to build the list of most common words in the index.

        Before using this application you need to generate the results
        files containing the text detections for each image in the dataset.

        It takes the path to the folder where the results are stored and
        the list of files inside the folder. The paths in the list of
        files should be relative to the results folder.

        A maximum of 250 common words is retrieved.

        See print_usage()
    """
    # Check proper usage
    if len(sys.argv) != 4:
        print_usage()
        exit(1)

    results_list = sys.argv[1]
    results_dir = sys.argv[2]
    out_file = sys.argv[3]

    print ("Reading text results from %s" % results_list)

    stopwords = ["a", "and", "are", "as", "at", "be",
            "but", "by", "for", "if", "in",
            "into", "is", "it", "no", "not",
            "of", "on", "or", "s", "such", "t",
            "that", "the", "their", "then",
            "there", "these", "they", "this",
            "to", "was", "will", "with", "",
            "www", "aleichem", ]

    # Read list of files
    res_fns = []
    with open(results_list, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            res_fns.append(row[0])
    print ("%d documents to add to analyze" % len(res_fns))

    # Read each file and keep count.  Note that the delimiter for
    # the input files is a "tab"
    c = Counter()
    for n, res_fn in enumerate(res_fns):
        print ("%d of %d" % (n+1, len(res_fns)))
        fn = os.path.join(results_dir, res_fn)

        words = []
        scores = []
        with open(fn, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
            for row in reader:
                words.append(row[0].lower())
                scores.append(int(round(float(row[1]))))

        for i, word in enumerate(words):
            # ignore numbers
            if word[0].isdigit():
                continue

            ws = word.split(' ')
            for w in ws:
                if len(w) > 3 and w not in stopwords:
                    c[w] += scores[i]

    # Build list of frequent words
    print ("Counting frequency of words...")
    most_common = c.most_common(250)
    most_common = [{'text': t[0].upper(), 'weight': math.exp(-0.1*i)} for i, t in enumerate(most_common)]

    # Finalize
    print ("Writing results to %s" % out_file)
    f = open(out_file, 'w+')
    j = json.dumps(most_common)
    f.write(j)
    f.close()

    print ("All done.")
