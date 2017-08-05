'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

from naive_dynamic_ix.memory_segment import MemorySegment
from naive_dynamic_ix.disk_segment import DiskSegment
from porter_stemmer import PorterStemmer
import re

class Index:
    '''
    Global index with underlying main index on disk and auxiliary index in memory.
    '''
    def __init__(self, filename):
        '''
        Creates an index with the given filename.
        :param filename: Filename to store the disk part of the index.
        '''
        self.disk_segment = DiskSegment.from_file(filename)
        self.memory_segment = MemorySegment()
        self.porter = PorterStemmer()
        self.memory_limit = 512000000 # arbitrary memory limit in bytes before writing index to disk

        with open("stopwords.dat", 'r') as f:
            stopwords = [line.rstrip() for line in f]
            self.stopwords = set(stopwords)

    def extract_terms(self, doc_str) -> list:
        doc_str = doc_str.lower()
        doc_str = re.sub(r'[^a-z0-9 ]', ' ', doc_str) # replace non-alphanumeric characters with whitespace
        terms = doc_str.split()
        terms = [t for t in terms if t not in self.stopwords]
        return [self.porter.stem(word, 0, len(word) - 1) for word in terms]  # return stemmed words

    def add_document(self, doc_str, doc_id):
        terms = self.extract_terms(doc_str)
        for pos, term in enumerate(terms):
            self.memory_segment.add_token(term, doc_id, pos)
        if self.memory_segment.get_size() >= self.memory_limit:
            self.save()

    def save(self):
        '''
        Saves any pending changes to disk and clears the memory portion of the index.
        :return: None
        '''
        self.memory_segment.merge_into_disk(self.disk_segment)
        self.memory_segment.clear()