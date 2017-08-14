'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

from naive_dynamic_ix.memory_segment import MemorySegment
from naive_dynamic_ix.disk_segment import DiskSegment
from naive_dynamic_ix.docstore import DocumentStore
from naive_dynamic_ix.results import Results
from porter_stemmer import PorterStemmer
import re

class Index:
    '''
    Global index with underlying main inverted index on disk and auxiliary inverted index in memory.
    '''
    def __init__(self, ix_filename, repo_filename):
        '''
        Creates an index and document store with the given filenames.
        :param ix_filename: Filename to store the disk part of the index.
        :param repo_filename: Filename to store the on-disk document store.
        '''
        self.docstore = DocumentStore.from_file(repo_filename)
        self.disk_segment = DiskSegment.from_file(ix_filename)
        self.memory_segment = MemorySegment()
        self.porter = PorterStemmer()
        self.memory_limit = 512000000 # arbitrary memory limit in bytes before writing index to disk

        with open("stopwords.dat", 'r') as f:
            stopwords = [line.rstrip() for line in f]
            self.stopwords = set(stopwords)

    def preprocess_term(self, term):
        term = term.lower()
        term = re.sub(r'[^a-z0-9 ]', '', term) # strip non-alphanumeric characters
        return self.porter.stem(term, 0, len(term) - 1)

    def extract_terms(self, doc_str) -> list:
        doc_str = doc_str.lower()
        doc_str = re.sub(r'[^a-z0-9 ]', ' ', doc_str) # replace non-alphanumeric characters with whitespace
        terms = doc_str.split()
        terms = [t for t in terms if t not in self.stopwords]
        return [self.porter.stem(word, 0, len(word) - 1) for word in terms]  # return stemmed words

    def add_document(self, doc_id, doc_title, doc_body):
        self.docstore.add_document(doc_id, doc_title, doc_body)
        terms = self.extract_terms(doc_title + " " + doc_body)
        for pos, term in enumerate(terms):
            self.memory_segment.add_token(term, doc_id, pos)
        if self.memory_segment.get_size() >= self.memory_limit:
            self.save()

    def do_free_text_query(self, terms: list) -> Results:
        '''
        Executes a free text query (searches for documents containing ANY of the terms)
        :param terms: List of the terms to search for.
        :return: Results object.
        '''
        terms = [self.preprocess_term(term) for term in terms if term not in self.stopwords]
        doc_ids = set()
        for term in terms:
            mem_results = self.memory_segment.do_one_word_query(term)
            disk_results = self.disk_segment.do_one_word_query(term)
            doc_ids |= set(mem_results)
            doc_ids |= set(disk_results)
        doc_ids = list(doc_ids)
        doc_titles = []
        snippets = []
        termset = set(terms)
        for doc_id in doc_ids:
            doc = self.docstore.get_document(doc_id)
            doc_titles.append(doc[0])
            snippets.append(self.get_result_snippet(termset, doc[1]))
        return Results(doc_ids, doc_titles, snippets)

    def do_phrase_query(self, terms: list) -> Results:
        '''
        Executes a phrase query (searches for documents containing the EXACT phrase)
        :param terms: List of terms comprising the phrase to search for.
        :return: Results object
        '''
        terms = [self.preprocess_term(term) for term in terms if term not in self.stopwords]
        doc_ids = set(self.memory_segment.do_phrase_query(terms)) | set(self.disk_segment.do_phrase_query(terms))
        doc_ids = list(doc_ids)
        doc_titles = []
        snippets = []
        termset = set(terms)
        for doc_id in doc_ids:
            doc = self.docstore.get_document(doc_id)
            doc_titles.append(doc[0])
            snippets.append(self.get_result_snippet(termset, doc[1]))
        return Results(doc_ids, doc_titles, snippets)

    def save(self):
        '''
        Saves any pending changes to disk and clears the memory portion of the index.
        :return: None
        '''
        self.memory_segment.merge_into_disk(self.disk_segment)
        self.memory_segment.clear()

    def get_result_snippet(self, termset: set, doc_body: str):
        '''
        Returns the minimum snippet of the document that contains all of the given terms (possibly in lemmatized form).
        :param termset: Set of the terms to search for.
        :param doc_body: Document text that contains the terms.
        :return: String snippet of minimum length containing all the terms in termset.
        '''
        # TODO. will just return first 400 chars for now.
        return doc_body[:400]
