import re
import collections
import heapq

import numpy as np
from nltk.corpus import stopwords
from nltk import PorterStemmer
import pysolr
import pprint
import json

# returns a list of tokens
def tokenize_doc(doc_text, stop_words):
    # doc_text = doc_text.replace('\n', ' ')
    # doc_text = " ".join(re.findall('[a-zA-Z]+', doc_text))
    # tokens = doc_text.split(' ')
    tokens = []
    text = doc_text
    text = re.sub(r'[\n]', ' ', text)
    text = re.sub(r'[,-]', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub('[0-9]', '', text)
    text = text.lower()
    tkns = text.split(' ')
    tokens = [token for token in tkns if token not in stop_words and token != '' and not token.isnumeric()]
    return tokens

def build_association(id_token_map, vocab, query):
    association_list = []
    for i, voc in enumerate(vocab):
        for word in query.split(' '):
            c1, c2, c3 = 0, 0, 0
            for doc_id, tokens_this_doc in id_token_map.items():
                count0 = tokens_this_doc.count(voc)
                count1 = tokens_this_doc.count(word)
                c1 += count0 * count1
                c2 += count0 * count0
                c3 += count1 * count1
            c1 /= (c1 + c2 + c3)
            #print(c1)
            if c1 != 0:
                association_list.append((voc, word, c1))

    return association_list

	
def association_main(query, solr_results):
    stop_words = set(stopwords.words(['english','spanish','italian', 'french', 'german', 'portuguese']))
    print(query)
    tokens = []
    token_counts = {}
    tokens_map = {}
    # tokens_map = collections.OrderedDict()
    document_ids = []

    for result in solr_results:
        #print(result['digest'])
        tokens_this_document = tokenize_doc(result['content'], stop_words)
        tokens_map[result['digest']] = tokens_this_document
        #print(tokens_this_document[:5])
        tokens.append(tokens_this_document)

    vocab = set([token for tokens_this_doc in tokens for token in tokens_this_doc])
    association_list = build_association(tokens_map, vocab, query)
    association_list.sort(key = lambda x: x[2],reverse=True)

    porter_stemmer = PorterStemmer()
    association_words = []
    for items in association_list:
        association_words.append(items[0])
    association_word_stems = [porter_stemmer.stem(word) for word in association_words]
    association_word_stems = list(set(association_word_stems))
    i = 0
    
    query_stems = [porter_stemmer.stem(word) for word in query.split(' ')]
    query_stems = list(set(query_stems))
    while(i<min(2, len(association_words))):
        for word in association_words:
            if word not in query.split(' ') and porter_stemmer.stem(word) not in query_stems:
                query_stems.append(porter_stemmer.stem(word))
                query += ' '+ word
                i +=1
                break
    print(query_stems)
    return query


# query = "content:opera"
# solr_results = get_results_from_solr(query, 20)
# #print(len(solr_results))
# print(association_main(query,solr_results))    