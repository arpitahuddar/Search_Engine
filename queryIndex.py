import timeit
import math
import json
import sys
from create_index import tokenize
from collections import OrderedDict
import itertools

indexFile = "index.json"

index = {}
parsed_json = {}

def getIndexFromFile():
	global index, parsed_json
	f = open (indexFile,'r')
	index = json.loads(f.read())
	#Getting URLs from bookkeeping file
	bookkeeping = open('WEBPAGES_CLEAN/bookkeeping.json')
	json_string = bookkeeping.read()
	parsed_json = json.loads(json_string)

def norm_l2(vec):
  sum = 0
  for val in vec:
    sum = sum + val**2
  return math.sqrt(sum)

def frequency_list(doc):
    tokens = tokenize(doc)
    dictionary={}
    for token in tokens:
        if token in dictionary:
            dictionary[token] = dictionary[token]+1
        else:
            dictionary[token] =1
    #print ("VALUES "+str(dictionary.values()))
    return dictionary.values()

def calcScore(result, queryString):
    global index
    tf_idf_d = 0
    queryScore = {}
    vec = []
    query_list = queryString.split()
    for word in query_list:
      vec.append(query_list.count(word))
    #print result
    for i,doc in enumerate(result):
        dot_prod = 0
        l_query = 0
        l_doc = 0
        for word in queryString.split() :
            idf = math.log(N/len(index[word]),2)
            if len(index[word][doc])<2:
                tf = math.log((1+len(index[word][doc][0])),2)
                #print(word + doc + " TF "+ str(tf))
                tf_idf_d = (tf/norm_l2(frequency_list(doc)))*idf
                #print(word + "TF-IDF" + str(tf_idf_d))
                index[word][doc].append(tf_idf_d)
            tf_idf_q = (query_list.count(word)/norm_l2(vec)) * idf
            prod = tf_idf_q * tf_idf_d
            dot_prod += prod
            l_query += tf_idf_q ** 2
            l_doc += tf_idf_d ** 2

        l_query = math.sqrt(l_query)
        l_doc = math.sqrt(l_doc)

        if not (l_query == 0 or l_doc == 0):
          cosine = dot_prod / (l_query * l_doc)
          queryScore[doc]=cosine
    queryScore = OrderedDict(sorted(queryScore.items(), key=lambda (k,v): (v,k) , reverse=True))
    queryScore = OrderedDict(itertools.islice(queryScore.items(),0,5))#???
    return queryScore

def queryWord(query):
	global index
	word = query.strip().lower()
	if word in index.keys():
		return [doc for doc in index[word].keys()]
	else:
		return []

def multipleQueryWords(queryString):
    result = []
    for word in queryString.split():
        result+=queryWord(word)
    return list(set(result))

def phraseQuery(queryString):
	global index
	queryString = queryString.lower()
	listOfLists, result = [],[]
	for word in queryString.split():
		listOfLists.append(queryWord(word))
	commonList = set(listOfLists[0]).intersection(*listOfLists)
	for doc in commonList:
		res = []
		for word in queryString.split():
		    res.append(index[word][doc][:])
		for i in range(len(res)):
			for ind in range(len(res[i])):
				res[i][ind][0] -=i
		if set(res[0][0]).intersection(*res[0][:]):
			result.append(doc)
	result_dict=calcScore(result,queryString)
	return result_dict#calcScore(result,queryString)

def Json_to_URL(result):
	global parsed_json
	URLs = []
	for doc_ID in result :
		URLs.append(parsed_json[doc_ID])
	return URLs

if __name__ == '__main__':
    query = sys.argv[1]
    start = timeit.default_timer()
    N=75*500-3
    getIndexFromFile()
    result = phraseQuery(query)
    print "Query results for",query
    #print "\n"
    print result
    URLs = Json_to_URL(result.keys())
    for url in URLs:
        print("URL --> " + url + "\n")
    #print "Size of Index", sys.getsizeof(index)*.001
    #print "Number of Unique words",len(index)
    #print "Number of documents",N
    stop = timeit.default_timer()
    run_time = stop - start
    print "run time is "+str(run_time)