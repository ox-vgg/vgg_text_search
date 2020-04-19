__author__      = 'Ernesto Coto'
__copyright__   = 'January 2020'

import os
import math
import multiprocessing
import simplejson as json
import settings
import re
import lucene

from java.nio.file import Paths
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.store import FSDirectory
from org.apache.lucene.index import DirectoryReader


class TextRetrieval(object):
    """
        Class for performing a search on an index of text detections
        with bounding boxes.
    """

    def init_index(self):
        """
            Initializes the lucene index, as well as creates an StandardAnalyzer and an IndexSearcher.
            Returns:
                vm: The initialized Java VM
                analyzer: StandardAnalyzer word analizer.
                searcher: Searcher over the lucene index.
        """
        self.vm = lucene.initVM(vmargs=['-Djava.awt.headless=true'])
        ldir = FSDirectory.open(Paths.get(settings.LUCENE_INDEX))
        self.analyzer = StandardAnalyzer()
        self.searcher = IndexSearcher(DirectoryReader.open(ldir))
        #self.searcher = IndexSearcher(ldir, readOnly=True)


    def prepare_success_json_str_(self, success):
        """
            Creates JSON with ONLY a 'success' field
            Parameters:
                Parameters: Boolean value for the 'success' field
            Returns:
                JSON formatted string
        """
        retfail = {}
        retfail['success'] = success
        return json.dumps(retfail)


    def testFunc(self, req_params):
        """
            Simple test function that will return the same JSON object
            as in the parameter. It can be used to test serve_request()
            Parameters:
                req_params: JSON object
            Returns:
                JSON formatted string
        """
        return json.dumps(req_params)


    def serve_request(self, request, pid):
        """
            Redirects a request to the correspondent function
            Parameters:
                request: JSON object with at least the fields:
                        - 'pid': A simple ID for the current process
                        - 'func': Name of the function to be invoked
            Returns:
                JSON containing the response of the invoked function,
                or JSON with the 'success' field set to 'False' if the
                function is not supported.
        """
        req_params = json.loads(request)
        req_params['pid'] = pid
        if 'func' in req_params:
            method = getattr(self, req_params['func'])
            if method:
                rval = method(req_params)
                return rval
            else:
                return self.prepare_success_json_str_(False)

        else:
            return self.prepare_success_json_str_(False)


    def do_query(self, query_string, page, numpp = 102, max_results=10000):
        """
            Performs the text query within the Lucene index.
            Parameters:
                query_string: Text to look for.
                page: Number of results page to return.
                numpp: Number of results per page.
                max_results: Maximum number of results to retrieve.
            Returns:
                A list of result items, each with information about a resulting frame.
                This information includes the path to the frame and its score.
        """
        self.vm.attachCurrentThread()
        query = QueryParser( "text", self.analyzer).parse(query_string)
        hits = self.searcher.search(query, max_results)
        results = []
        num_ims = len(hits.scoreDocs)
        num_pages = 0
        if num_ims>0:
            numpp = min(numpp, num_ims)
            num_pages = math.ceil(float(num_ims) / float(numpp))
            pagestart = numpp * (page-1)
            pageend = pagestart + numpp
            for i, hit in enumerate(hits.scoreDocs):
                if i >= pageend:
                    break
                if i < pagestart:
                    continue
                result = {
                    'score': hit.score,
                }
                doc = self.searcher.doc(hit.doc)
                result['frame'] = doc.getField('frame').stringValue()
                results.append(result)
        return results, num_pages, num_ims


    def do_autocomplete_query(self, query_string, max_results=10):
        """
            Retrieves a list of words that contain the 'query_string'.
            By default, a maximum of 10 words is returned.
            Parameters:
                query_string: Text for the query
                max_results: Maximum number of results in the list
            Returns:
                List of query results
        """
        self.vm.attachCurrentThread()
        # Add a '*' to get more results
        query = QueryParser("text", self.analyzer).parse(query_string + '*')
        hits = self.searcher.search(query, max_results*max_results)
        results = []
        for hit in hits.scoreDocs:
            doc = self.searcher.doc(hit.doc)
            indexed_text = doc.getField('text').stringValue()
            if indexed_text:
                # When added to the index, text is repeated by their frequency, undo that here.
                # Plus, take the opportunity to make text lowercase too
                indexed_text = indexed_text.split(' ')
                for word in indexed_text:
                    # Now check the query string is actually present in the suggestion, and
                    # the suggestion does not contain problematic characters
                    word = word.lower()
                    if word.startswith(query_string.lower()) and (
                       re.match("^[#$]?[a-zA-Z0-9_\-\ +,:;.!\?()\[\]]*$", word)):
                        results.append(word)
        # Remove repeated results and crop the list to a max length of max_results
        non_repeated_results = list(dict.fromkeys(results))[:max_results]
        return non_repeated_results


    def __init__(self):
        """
            Initializes an instance of this class
        """
        self.query_id = 0
        self.query_data = dict()
        self.query_id_lock = multiprocessing.Lock()
        self.init_index()
        print ("TextRetrieval successfully initialized")


    def getSearchSuggestions(self, req_params):
        """
            Retrieves a list of words that starts with the 'query_string' specified
            in the request.
            This method is specific to the TextRetrieval, as other
            backends do not supply a list of suggestions for a text query.
            Parameters:
                req_params: JSON object with at least the field 'query_string'.
            Returns:
                JSON formatted string in the form '{ 'results': <list of results> }'.
                <list of results> is sorted by string length.
        """
        print ('**** getSearchSuggestions')

        results = []
        if 'query_string' in req_params:
            query = req_params['query_string']
            try:
                results = self.do_autocomplete_query(query)
                results.sort(key=len)  # sort by length
            except:
                results = []

        return json.dumps( {'success':True, 'results': results} )


    def getRoi(self, req_params):
        """
            Retrieves the detection ROI for a word within an image (frame).
            If the word is found several times withing the image, it returns
            the ROI of the detection with the highest score.
            Parameters:
                req_params: JSON object with at least the fields:
                    frame_path: Path to the source image.
                    query_string: Text to look for within the words detected in the input image.
            Returns:
                A list with the coordinates of the ROI in the form of a bounding box
                [top-rigth-x, top-rigth-y, bottom-left-x, bottom-left-y]. The list
                is returned in string form, coordinates are separated by '_'.
        """
        print ('**** getRoi')

        roi_string = ''
        try:
            query_string = req_params['query_string']
            frame_path = req_params['frame_path']
            with open(os.path.join(settings.TEXT_RESULTS_DIR, frame_path + '.txt'), 'r') as csvfile:
                best_score = -1
                for line in csvfile:
                    if len(line)>0:
                        # With the instruction below, note that the ROI won't be found
                        # unless the coordinates are separated by "tab" in the text results files.
                        # See the code of the "index_results" utility script.
                        values = line.split('\t')
                        word = values[0]
                        if query_string.lower() in word.lower():
                            score = float(values[1])
                            if score > best_score:
                                selXMin = int(round(float(values[2])))
                                selYMin = int(round(float(values[3])))
                                selXMax = str( selXMin + int(round(float(values[4]))) )
                                selYMax = str( selYMin + int(round(float(values[5]))) )
                                selXMin = str(selXMin)
                                selYMin = str(selYMin)
                                roi_string = selXMin+'_'+selYMin + '_' + selXMin+'_'+ \
                                             selYMax + '_' + selXMax+'_'+selYMax + '_' + \
                                             selXMax+'_'+selYMin + '_' + selXMin+'_'+selYMin
                                best_score = score
        except Exception as e:
            print (e)
            return self.prepare_success_json_str_(False)

        return json.dumps( { 'success':True, 'roi': roi_string} )


    def selfTest(self, req_params):
        """
            Returns a JSON string with 'success' field always 'True'
            Returns:
                JSON formatted string
        """
        print ("**** Server is running")
        return self.prepare_success_json_str_(True)


    def getQueryId(self, req_params):
        """
            Generates a new query ID and returns it.
            Parameters:
                req_params: JSON object with at least the field 'dataset'.
            Returns:
                JSON formatted string with the query id and the 'success' field.
        """
        print ('**** getQueryId')

        if 'dataset' in req_params:
            dataset = req_params['dataset']
        else:
            return self.prepare_success_json_str_(False)

        self.query_id_lock.acquire()
        self.query_id = self.query_id+1
        query_id = self.query_id;
        self.query_id_lock.release()

        self.query_data[str(query_id)] = dict()
        self.query_data[str(query_id)]['dataset'] = dataset
        return json.dumps( { 'success':True, 'query_id': query_id } )


    def releaseQueryId(self, req_params):
        """
            Deletes any data associated with a query ID.
            Parameters:
                req_params: JSON object with at least the field 'query_id'.
            Returns:
                JSON formatted string with 'success' field set to 'False'
                in case of any problems. The 'success' field set to 'True'
                otherwise.
        """
        print ('**** releaseQueryId')

        if 'query_id' in req_params:
            query_id = req_params['query_id']
        else:
            return self.prepare_success_json_str_(False)

        query_id = str(query_id)
        if query_id in self.query_data:
            try:
                del self.query_data[query_id]
                return self.prepare_success_json_str_(True)
            except:
                return self.prepare_success_json_str_(False)
        else:
            return self.prepare_success_json_str_(False)


    def addTrs(self, req_params, pos=True):
        # This backend does not need positive/negative images.
        # Just tell the frontend everything is ok.
        return self.prepare_success_json_str_(True)


    def addPosTrsAsync(self,req_params):
        # NOTE: This is a raw copy of addPosTrs() (i.e. NOT REALLY ASYNC)
        # added here for compatibility with the frontend
        # Add your async code here if possible
        return self.addTrs(req_params, True)


    def addPosTrs(self,req_params):
        # This backend does not need positive/negative images.
        # Just tell the frontend everything is ok.
        return self.addTrs(req_params, True)


    def addNegTrs(self,req_params):
        # Not needed for this backend.
        # Return error if used, as it should not be called
        return self.addTrs(req_params, False)


    def train(self,req_params):
        """
            Performs the actual search on the index. Returns a list
            of images containing the query string.
            Parameters:
                req_params: JSON object with at least the field 'query_id',
                            and either 'query_string' or 'anno_path'.
            Returns:
                JSON formatted string with 'success' field set to 'False'
                in case of any problems. The 'success' field set to 'True'
                otherwise.
        """
        print ('**** train')

        if 'query_id' in req_params:
            query_id = req_params['query_id']
        else:
            return self.prepare_success_json_str_(False)

        try:

            query_id = str(query_id)
            query_string = None
            if 'query_string' in self.query_data[query_id]:
                query_string = self.query_data[query_id]['query_string']
            elif 'anno_path' in req_params:
                # extract query text from annotation filepath
                annofile = req_params['anno_path']
                basename = os.path.basename(annofile)
                query_string = basename.split('.')[0]
                query_string = query_string.replace('text__','')
                query_string = query_string[1:]
                query_string = query_string[:-1]
                self.query_data[query_id] ['query_string'] = query_string
            else:
                print ('Could not found query string')
                return self.prepare_success_json_str_(False)

            print ("Performing search for text:", query_string)
            # Forcing a maximum of settings.MAX_RESULTS_RETURN results,
            # returned in a single list. Let the frontend do the paging.
            results, num_pages, num_ims = self.do_query(query_string,
                    page = 1,
                    numpp = settings.MAX_RESULTS_RETURN,
                    max_results = settings.MAX_RESULTS_RETURN)
            self.query_data[query_id]["results"] = results

            return self.prepare_success_json_str_(True)
        except Exception as e:
            print (e)
            return self.prepare_success_json_str_(False)


    def loadClassifier(self, req_params):
        # Not needed for this backend.
        # Just tell the frontend everything is ok.
        return self.prepare_success_json_str_(True)


    def saveClassifier(self, req_params):
        # Not needed for this backend.
        # Just tell the frontend everything is ok.
        return self.prepare_success_json_str_(True)


    def getAnnotations(self,req_params):
        # Not needed for this backend.
        # Just tell the frontend everything is ok.
        return self.prepare_success_json_str_(True)


    def saveAnnotations(self, req_params):
        """
            Invoked by the frontend to create an annotations file with
            training information. However, that concept does not apply
            to the text-retrieval backend, so this method is used to
            extract the query string from the path to the annotations
            file, in preparation for the call to rank()
            Parameters:
                req_params: JSON object with at least the 'query_id'
                            and 'filepath' fields.
            Returns:
                JSON formatted string with 'success' field set to 'False'
                in case of any problems. The 'success' field set to 'True'
                otherwise.
        """
        print ('**** saveAnnotations')

        if 'query_id' in req_params:
            query_id = req_params['query_id']
        else:
            return self.prepare_success_json_str_(False)

        if 'filepath' in req_params:
            annofile = req_params['filepath']
        else:
            return self.prepare_success_json_str_(False)

        try:
            # extract query text from annotation filepath
            basename = os.path.basename(annofile)
            query_string = basename.split('.')[0]
            query_string = query_string.replace('text__','')
            query_string = query_string[1:]
            query_string = query_string[:-1]
            self.query_data[str(query_id)]['query_string'] = query_string
            return self.prepare_success_json_str_(True)
        except:
           return self.prepare_success_json_str_(False)


    def rank(self, req_params):
        """
            Sorts the results by score. However, the index already sorts
            the query results, so this method is used to convert the
            results to a format the frontend understands, in preparation
            for the call to getRanking()
            Parameters:
                req_params: JSON object with at least the field 'query_id'.
            Returns:
                JSON formatted string with 'success' field set to 'False'
                in case of any problems. The 'success' field set to 'True'
                otherwise.
                The list of images is returned in the 'rankings' field.
        """
        print ('**** rank')

        if 'query_id' in req_params:
            query_id = req_params['query_id']
        else:
            return self.prepare_success_json_str_(False)

        print ("Results already ranked.")
        print ("Converting results to frontend format.")
        query_id = str(query_id)
        self.query_data[query_id]["rankings"] = []
        for result in self.query_data[query_id]["results"]:
            item = dict()
            item['path'] = result['frame']
            if item['path'].startswith('./'):
                # remove the ./ at the beginning of each frame path
                item['path'] = result['frame'][2:]
            item['score'] = result['score']
            self.query_data[query_id]["rankings"].append(item)

        return self.prepare_success_json_str_(True)


    def getRanking(self, req_params):
        """
            Retrieves the ranked results.
            Parameters:
                req_params: JSON object with at least the field 'query_id'.
            Returns:
                JSON formatted string with 'success' field set to 'False'
                in case of any problems. The 'success' field set to 'True'
                otherwise.
                The results are returned in the 'rankings' field.
        """
        print ('**** getRanking')

        if 'query_id' in req_params:
            query_id = req_params['query_id']
        else:
            return self.prepare_success_json_str_(False)

        query_id = str(query_id)
        if query_id in self.query_data:
            if "rankings" in self.query_data[query_id]:
                return json.dumps( { 'success': True, 'ranklist': self.query_data[query_id]["rankings"] } )
            else:
                return self.prepare_success_json_str_(False)
        else:
            return self.prepare_success_json_str_(False)


    def loadAnnotationsAndTrs(self,req_params):
        # Not needed for this backend.
        # Return error if used, as it should not be called
        return self.prepare_success_json_str_(False)


    def getRankingSubset(self,req_params):
        # Not needed for this backend.
        # Return error if used, as it should not be called
        return self.prepare_success_json_str_(False)

