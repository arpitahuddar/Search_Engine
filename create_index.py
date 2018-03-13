import re
import timeit
import math
import json
from nltk.stem import WordNetLemmatizer

indexes = "Indexes/"
filepath1 = "WEBPAGES_CLEAN/"
indexFile = "index.json"
stopwordsFile = "stopwords.txt"

index={}
stopwords = []
lemmatizer = WordNetLemmatizer()

def getStopwords():
    #get stopwords from the stopwords file
    global stopwords
    f=open(stopwordsFile, 'r')
    stopwords=[line.rstrip() for line in f]
    f.close()
#returns list of all terms in documents
def tokenize(doc_id):
    global stopwords
    filepath=filepath1+doc_id
    f = open(filepath,"r")
    tokens = []
    lines = f.readlines()
    for line in lines:
        line = line.decode('utf-8').strip().lower().split()
        line=[x for x in line if x not in stopwords]
        #line=[ lemmatizer.lemmatize(word) for word in line ]
        words = re.findall(r"[\w]+", ' '.join(line))
        tokens.extend(words)
    return tokens


#returns map of words and their positions in document    
def addTokensToIndex(tokens,doc_id):
    global index
    for i,token in enumerate(tokens):
        if token not in index:
            index[token]={doc_id:[[i]]}
        else:
            if doc_id in index[token].keys():
                index[token][doc_id][0].append(i)
            else:
                index[token][doc_id]=[[i]]

def writeIndexToFile():
    #writes term document postings to file in the format below
    # software, [9/9: [8, 213, 456]]
    global index
    f=open(indexFile, 'w')
    for term in index.iterkeys():
        postinglist=[]
        for doc in index[term]:
            docID=doc
            positions=index[term][doc]
            postinglist.append(':'.join([str(docID) ,','.join(map(str,positions))]))
            #print >> f, ''.join((term,'|',';'.join(postinglist)))
            f.write(''.join((term,'|',';'.join(postinglist))))
        f.write('\n')       
    f.close()


if __name__ == '__main__':

    getStopwords()
    start = timeit.default_timer()
    for i in range(1):
        for j in range(500):
            #doc_id taken as folderNumber/fileNumber. 0/0, 0/1 etc
            doc_id = str(i)+"/"+str(j)
            tokens = tokenize(doc_id)
            addTokensToIndex(tokens, doc_id)
    
    stop = timeit.default_timer()
    #writeIndexToFile()
    f=open(indexFile, 'w')
    f.write(json.dumps(index))
    f.close()
    run_time = stop - start
    print "run time is "+str(run_time)