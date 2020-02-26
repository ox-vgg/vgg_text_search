__author__      = 'Ernesto Coto'
__copyright__   = 'February 2020'

import sys
import csv
import shutil
import os
import lucene

from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.document import Document, Field, TextField, FieldType
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexOptions

def print_usage():
    print ("Application used to build the index for the text detections in the dataset of images.")
    print ("Usage:")
    print ("python %s results_list results_dir index_dir" % sys.argv[0])

if __name__ == "__main__":
    """
        Application used to build the index for the text detections in
        the dataset of images.

        Before using this application you need to generate the results
        files containing the text detections for each image in the dataset.

        It takes the path to the folder where the results are stored and
        the list of files inside the folder. The paths in the list of
        files should be relative to the results folder.

        See print_usage()
    """
    # Check proper usage
    if len(sys.argv) != 4:
        print_usage()
        exit(1)

    results_list = sys.argv[1]
    results_dir = sys.argv[2]
    index_dir = sys.argv[3]
    print ("Creating Lucene index for %s in %s" % (results_list, index_dir))

    # Check if the index already exists...
    opt = "r"
    if os.path.isdir(index_dir):
        # ... and "add" or "replace" if needed
        opt = input("Index already exists, replace (r) or add (a)? [r]: ")
        if not len(opt) or opt == "r":
            shutil.rmtree(index_dir)

    # Init lucene stuff
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    ldir = SimpleFSDirectory(Paths.get(index_dir))
    # create and open an index writer
    config = IndexWriterConfig(LimitTokenCountAnalyzer(StandardAnalyzer(), 512))
    if opt == "r":
        config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
    else:
        config.setOpenMode(IndexWriterConfig.OpenMode.APPEND)
    writer = IndexWriter(ldir, config)

    print ("Currently there are %d documents in the index..." % writer.docStats.numDocs)

    # Read the documents to be added to the index
    res_fns = []
    with open(results_list, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            res_fns.append(row[0])
    print ("%d documents to add to the index" % len(res_fns))

    # Add the new documents. Note that the delimiter for
    # the input files is a "tab"
    for n, res_fn in enumerate(res_fns):
        print ("%d of %d" % (n+1, len(res_fns)))
        fn = os.path.join(results_dir, res_fn)

        words = []
        scores = []
        bbs = []
        with open(fn, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
            for row in reader:
                words.append(row[0])
                scores.append(int(round(float(row[1]))))
                bbs.append([int(round(float(row[2]))),
                            int(round(float(row[3]))),
                            int(round(float(row[4]))),
                            int(round(float(row[5])))])

        im_text = ""
        annotation = {}
        for i, word in enumerate(words):
            # ignore numbers
            if word[0].isdigit():
                continue
            # multiply by frequency occurring
            im_text += (word + " ") * scores[i]
            if word not in annotation:
                annotation[word] = {
                    'score': scores[i],
                    'bb': bbs[i],
                }

        doc = Document()
        doc.add(TextField("text",im_text, Field.Store.YES))
        t1 = FieldType()
        t1.setStored(True)
        t1.setTokenized(False)
        t1.setIndexOptions(IndexOptions.NONE)
        doc.add(Field("frame", res_fn.replace('.txt', ''), t1))
        writer.addDocument(doc)

    # Clean up and finalize
    print ("Optimizing index of %d documents..." % writer.docStats.numDocs)
    writer.forceMerge(1, True)
    print ("Closing index %s" % index_dir)
    writer.close()
    print ("Finished.")
