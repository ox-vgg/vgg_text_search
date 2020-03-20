__author__      = 'Ernesto Coto'
__copyright__   = 'February 2020'

import sys
import lucene

from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.index import DirectoryReader

def print_usage():
    print ("Simple console application to perform a search in the index")
    print ("Usage:")
    print ("python %s index_dir" % sys.argv[0])

if __name__ == "__main__":
    """
        Simple console application to perform a search in the index.
        It takes the path to the index folder.
        The user can perform consecutive searches until and then exit
        the program when no longer needed.
        For each result, this script prints the score of the search
        and the text found.

        See print_usage()
    """
    # Check proper usage
    if len(sys.argv) != 2:
        print_usage()
        exit(1)

    # Init lucene stuff
    index_dir = sys.argv[1]
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    ldir = SimpleFSDirectory(Paths.get(index_dir))
    analyzer = StandardAnalyzer()
    searcher = IndexSearcher(DirectoryReader.open(ldir))

    # Request search term until the user decides to stop the process
    while True:
        opt = input("Search: ")
        if not opt:
            break
        query = QueryParser("text", analyzer).parse(opt + '*')
        MAX = 100
        hits = searcher.search(query, MAX)

        doc_counter = 0
        for hit in hits.scoreDocs:
            doc = searcher.doc(hit.doc)
            words = doc.getField('text').stringValue()
            img = doc.getField('frame').stringValue()
            if opt.lower() in words.lower():
               doc_counter = doc_counter + 1
               for word in words.split(' '):
                   if opt.lower() in word.lower():
                       doc_counter = doc_counter + 1
                       print ("score:", hit.score, "text:", word, "frame:", img)

        print ("Found %d documents for '%s'" % (doc_counter, query))
