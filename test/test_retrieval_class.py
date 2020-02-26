__author__      = 'Ernesto Coto'
__copyright__   = 'January 2020'

import os
import sys
import argparse

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(FILE_DIR, '..', 'service'))
from text_retrieval import TextRetrieval

"""
    Utility function to test the face retrieval without using sockets.
    Use this function to test separately from the frontend.
"""

if __name__ == "__main__":
    """ Main method """

    # Parse arguments
    parser = argparse.ArgumentParser(description='vgg_text_index test script for the face retrieval class')
    parser.add_argument('text_query', metavar='text_query', type=str,
        help='Text query to perform on the dataset')
    args = parser.parse_args()

    backend_instance = TextRetrieval()
    backend_instance.selfTest(None)

    # start query
    response = backend_instance.getQueryId( {'pid': 8475, 'func': 'getQueryId', 'dataset': 'mydataset'} )
    print ('response:', response)

    # saveAnnotations
    response = backend_instance.saveAnnotations( {'pid': 8475, 'query_id': 1,
             'func': 'saveAnnotations',
             'filepath': 'some/path/text__{%s}.txt' % args.text_query  # extracts text query string from fake filepath
    })
    print ('response:', response)

    # train
    response = backend_instance.train( {'pid': 8475, 'query_id': 1, 'func': 'train'} )
    print ('response:', response)

    # rank
    response = backend_instance.rank({'pid': 8475, 'query_id': 1, 'func': 'rank'})
    print ('response:', response)

    # getRanking
    response = backend_instance.getRanking({'pid': 8475, 'query_id': 1, 'func': 'getRanking'})
    print ('response:', response)

    # releaseQueryId
    response = backend_instance.releaseQueryId({'pid': 8475, 'query_id': 1, 'func': 'releaseQueryId'})
    print ('response:', response)
