'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

import bsddb3
from pickle import dumps, loads
from naive_dynamic_ix.memory_segment import PostingList

from naive_dynamic_ix.results import Results
class DiskSegment:
    def __init__(self, bsddb):
        self.index = bsddb

    @classmethod
    def from_file(cls, filename: str):
        '''
        Reads in an index file to create a new disk segment, or creates the file if it does not exist.
        :param filename: str - the filename of the index.
        :return: DiskSegment object.
        '''
        bsddb = bsddb3.hashopen(filename, 'c')
        return cls(bsddb)

    def do_one_word_query(self, term: str) -> Results:
        '''
        Executes a one word query on the index with the given term.
        :param term: str
        :return: Results object with doc ids but not results snippets.
        '''
        posting_list = self.index[term]
        doc_ids = [posting.doc_id for posting in posting_list]
        return Results(doc_ids)

    def do_phrase_query(self, terms: list) -> Results:
        '''
        Executes a phrase query on the index with the given sequence of terms.
        :param terms: List of strings representing the exact phrase in order.
        :return: Results object with doc ids but not results snippets.
        '''
        posting_list = loads(self.index[dumps(terms[0])])
        # TODO

    def iteritems(self):
        '''
        Supplies a generator over the items in the disk segment.
        :return: A generator over the index's items.
        '''
        return self.index.iteritems()

    def merge_posting_list(self, term: str, posting_list: PostingList):
        '''
        Merges the given PostingList for the given term into the on-disk segment.
        :param term: str
        :param posting_list: PostingList
        :return: None
        '''
        pass