'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

import bsddb3
from pickle import dumps, loads
from naive_dynamic_ix.memory_segment import PostingList

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

    def do_one_word_query(self, term: str) -> list:
        '''
        Executes a one word query on the index with the given term.
        :param term: str
        :return: List of matching doc ids.
        '''
        try:
            posting_list = loads(self.index[dumps(term)])
            doc_ids = [posting.doc_id for posting in posting_list.postings]
            return doc_ids
        except KeyError:
            return []

    def do_phrase_query(self, terms: list) -> list:
        '''
        Executes a phrase query on the index with the given sequence of terms.
        :param terms: List of strings representing the exact phrase in order.
        :return: List of matching doc ids.
        '''
        posting_lists = [loads(self.index[dumps(t)]) if self.has_key(t) else PostingList()
                         for t in terms]
        result_pl = PostingList.find_phrases(posting_lists)
        doc_ids = [posting.doc_id for posting in result_pl.postings]
        return doc_ids

    def has_key(self, term: str):
        '''
        :param term: The term to search for the index
        :return: term is in the index or not.
        '''
        return self.index.has_key(dumps(term))

    def keys(self):
        '''
        Supplies a generator over the keys in the disk segment.
        Note that all keys are pickled and must be loaded().
        :return: A generator over the index's keys.
        '''
        return self.index.keys()

    def merge_posting_list(self, term: str, posting_list: PostingList):
        '''
        Merges the given PostingList for the given term into the on-disk segment.
        :param term: str
        :param posting_list: PostingList
        :return: None
        '''
        if self.has_key(term):
            disk_pl = loads(self.index[dumps(term)])
            merged_pl = PostingList.merge_lists(disk_pl, posting_list)
            self.index[dumps(term)] = dumps(merged_pl)
        else:
            self.index[dumps(term)] = dumps(posting_list)