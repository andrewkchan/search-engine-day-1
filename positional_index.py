'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

from collections import defaultdict
from bisect import bisect_left

class Token:
    def __init__(self, term: str, doc_id: int, position: int):
        self.term = term
        self.doc_id = doc_id
        self.position = position

class Posting:
    def __init__(self, doc_id: int, positions: list):
        '''
        A Posting maintains a sorted position list corresponding to a document id.
        '''
        self.doc_id = doc_id
        self.positions = positions
    def add_position(self, position: int):
        '''
        Insert the given position into the sorted position list iff the position is not already in the list.
        '''
        position_i = bisect_left(self.positions, position)
        if self.positions[position_i] != position:
            self.positions.insert(position_i, position)
    def merge_posting(self, posting: Posting):
        '''
        Merge the positions lists of 2 postings.
        '''
        #TODO

class PostingList:
    def __init__(self):
        '''
        A PostingList maintains a list of Posting objects sorted by doc_id.
        '''
        self.postings = []
        self.__doc_ids = [] # keep a separate list of doc ids mostly for convenience to use with bisect_left.
    def add_posting(self, posting: Posting):
        posting_i = bisect_left(self.__doc_ids, posting.doc_id)
        if self.__doc_ids[posting_i] != posting.doc_id:
            self.postings.insert(posting_i, posting)
        else:
            self.postings[posting_i].merge_posting(posting)


class PositionalIndex:
    def __init__(self):
	    self.index = defaultdict(list)
    def add_token(self, term: str, doc_id: int, position: int):
        '''
        Adds a token to the index.
        A Token is a (term, doc_id, position) triplet, indicating that the term occurred in
        the document corresponding to doc_id at the given position.
        '''

        # TODO
