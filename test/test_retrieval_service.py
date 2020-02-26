__author__      = 'Ernesto Coto'
__copyright__   = 'January 2020'

import os
import sys
import argparse
import socket
import json

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(FILE_DIR, '..', 'service'))
import settings

# Network communication constants
BUFFER_SIZE = 1024
TCP_TERMINATOR = '$$$'
TCP_TIMEOUT = 86400.00

"""
    Utility function to test the text retrieval service.
    Use this function to simulate the calls from the frontend.
"""

def custom_request(request, append_end=True):
    """
        Sends a request to the host and port specified in the backend settings
        Arguments:
            request: JSON object to be sent
            append_end: Boolean to indicate whether or not to append
                        a TCP_TERMINATOR value at the end of the request.
        Returns:
            JSON containing the response from the host
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((settings.HOST, settings.PORT))
    except socket.error as msg:
        print ('Connect failed', msg)
        return False

    sock.settimeout(TCP_TIMEOUT)

    print ('Request to backend at port %s: %s' % (str(settings.PORT), request))

    if append_end:
        request += TCP_TERMINATOR
    total_sent = 0
    while total_sent < len(request):
        sent = sock.send(request[total_sent:].encode())
        if sent == 0:
            raise RuntimeError("Socket connection broken at port " + str(settings.PORT))
        total_sent = total_sent + sent

    term_idx = -1
    response = ''
    while term_idx < 0:
        try:
            rep_chunk = sock.recv(BUFFER_SIZE)
            if not rep_chunk:
                print ('Connection closed! at port ' + str(settings.PORT))
                sock.close()
                return False
            response = response + rep_chunk.decode()
            term_idx = response.find(TCP_TERMINATOR)
        except socket.timeout:
            print ('Socket timeout at port ' + str(self.port))
            sock.close()
            return False

    excess_sz = term_idx + len(TCP_TERMINATOR)
    response = response[0:term_idx]
    sock.close()

    return response

if __name__ == "__main__":
    """ Main method """

    # Parse arguments
    parser = argparse.ArgumentParser(description='vgg_text_index test script for the face retrieval service')
    parser.add_argument('text_query', metavar='text_query', type=str,
        help='Text query to perform on the dataset')
    args = parser.parse_args()

    # 1) Connect to backend and test connection

    print ('** Sending selfTest')
    req_obj = {'func': 'selfTest'}
    request = json.dumps(req_obj)
    response = custom_request(request)
    func_out = json.loads(response)
    print ('Received response:')
    print (func_out)

    # 2) Start a query by getting a query ID

    print ('** Sending getQueryId')
    req_obj = {'func': 'getQueryId', 'dataset': 'dummy'}
    request = json.dumps(req_obj)
    response = custom_request(request)
    func_out = json.loads(response)
    print ('Received response:')
    print (func_out)
    query_id = func_out['query_id']

    # 3) Train the classifier
    # Note that here we provide the annotation path in the same call to train()
    # to avoid calling saveClassifier() first.

    print ('** Sending train')
    req_obj = {'func': 'train',
               'anno_path': 'some/path/text__{%s}.txt' % args.text_query, # extracts text query string from fake filepath
               'query_id': query_id}
    request = json.dumps(req_obj)
    response = custom_request(request)
    func_out = json.loads(response)
    print ('Received response:')
    print (func_out)
    if not func_out['success']: raise RuntimeError("train")

    # 4) Rank results

    print ('** Sending rank')
    req_obj = {'func': 'rank',
               'query_id': query_id}
    request = json.dumps(req_obj)
    response = custom_request(request)
    func_out = json.loads(response)
    print ('Received response:')
    print (func_out)
    if not func_out['success']: raise RuntimeError("rank")

    # 5) Get ranked results

    print ('** Sending getRanking')
    req_obj = {'func': 'getRanking',
               'query_id': query_id}
    request = json.dumps(req_obj)
    response = custom_request(request)
    func_out = json.loads(response)
    print ('Received response:')
    if not func_out['success']: raise RuntimeError("getRanking")
    rank_result = func_out['ranklist']
    print (rank_result)
    print ('Retrieved %d results' % len(rank_result))

    # 6) Free the query in the backend to save memory

    print ('** Sending releaseQueryId')
    req_obj = {'func': 'releaseQueryId',
               'query_id': query_id}
    request = json.dumps(req_obj)
    response = custom_request(request)
    func_out = json.loads(response)
    print ('Received response:')
    print (func_out)
    if not func_out['success']: raise RuntimeError("releaseQueryId")
