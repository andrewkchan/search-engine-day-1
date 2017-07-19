#!/usr/bin/env python3

import sys
import re
from porter_stemmer import PorterStemmer

porter = PorterStemmer()
stopwords = ["the", "an", "and", "or", "where", "there", "in", "a", "that", "of", "it", "its", "to", "as", "by", "who", "what", "when", "with"]

def index_document(index, doc_id, docstring):
    '''
    Indexes the single given document, adding its entries to the existing index.
    @param
        index: dict
        doc_id: int
        docstring: str
    '''
    terms = get_terms(docstring) # parse docstring, normalize terms

    # add the doc id to each term's entry in the index
    for term in terms:
        if term not in index:
            index[term] = [doc_id]
        elif doc_id not in index[term]:
            index[term].append(doc_id)
    return index

def get_terms(docstring):
    docstring = docstring.lower()
    docstring = re.sub(r'[^a-z0-9 ]', ' ', docstring) # replace non-alphanumeric characters with whitespace
    terms = docstring.split()
    terms = [word for word in terms if word not in stopwords]
    return [porter.stem(word, 0, len(word) - 1) for word in terms] # return stemmed words
