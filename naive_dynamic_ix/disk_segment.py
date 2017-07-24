'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

import dbm
from naive_dynamic_ix.memory_segment import PostingList

from naive_dynamic_ix.results import Results
class DiskSegment:
    def __init__(self, gdbm):
        self.index = gdbm

    @classmethod
    def from_file(cls, filename: str):
        '''
        Reads in an index file to create a new disk segment, or creates the file if it does not exist.
        :param filename: str - the filename of the index.
        :return: DiskSegment object.
        '''
        gdbm = dbm.gnu.open(filename, 'c')
        return cls(gdbm)

    def do_one_word_query(self, term: str) -> Results:
        '''
        Executes a one word query on the index with the given term.
        :param term: str
        :return: Results object.
        '''
        posting_list = self.index[term]
        doc_ids = [posting.doc_id for posting in posting_list]
        return Results(doc_ids)

    def do_phrase_query(self, terms: list) -> Results:
        '''
        Executes a phrase query on the index with the given sequence of terms.
        :param terms: List of strings representing the exact phrase in order.
        :return: Results object.
        '''
        posting_list = self.index[terms[0]]
        # TODO

    def keys(self):
        '''
        Supplies a generator over the keys in the disk segment.
        :return: A generator over the index's keys.
        '''
        k = self.index.firstkey()
        while k != None:
            yield k
            k = self.index.nextkey(k)

    def merge_posting_list(self, term: str, posting_list: PostingList):
        '''
        Merges the given PostingList for the given term into the on-disk segment.
        :param term: str
        :param posting_list: PostingList
        :return: None
        '''
        pass