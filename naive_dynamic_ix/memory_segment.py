'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

from collections import defaultdict
from bisect import bisect_left

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

    def merge_posting(self, posting):
        '''
        Merge the positions lists of the input posting into our own position list.
        '''
        i, j = 0, 0
        merged = []
        while i < len(self.positions) or j < len(posting.positions):
            if i < len(self.positions):
                if j < len(posting.positions):
                    if self.positions[i] <= posting.positions[j]:
                        merged.append(self.positions[i])
                        i += 1
                    else:
                        merged.append(posting.positions[j])
                        j += 1
                else:
                    merged.append(self.positions[i])
                    i += 1
            else:
                merged.append(posting.positions[j])
                j += 1
        self.positions = merged

class PostingList:
    def __init__(self):
        '''
        A PostingList maintains a list of Posting objects sorted by doc_id.
        '''
        self.postings = []
        self.__doc_ids = [] # keep a separate list of doc ids mostly for convenience to use with bisect_left.

    def add_posting(self, posting: Posting):
        '''
        Adds a posting to the posting list, maintaining sorted order.
        :param posting: Posting object
        :return: None
        '''
        posting_i = bisect_left(self.__doc_ids, posting.doc_id)
        if self.__doc_ids[posting_i] != posting.doc_id:
            # if we don't already have this doc in our postings list, insert it
            self.postings.insert(posting_i, posting)
        else:
            # if already have this doc, merge the positions lists of the postings
            self.postings[posting_i].merge_posting(posting)

    def phrase_intersect(self, posting_list):
        '''
        Executes an exact phrase intersection with another posting list, modifying self in-place.
        :param posting_list: Another PostingList.
        :return: None
        '''
        # TODO

from naive_dynamic_ix.results import Results
class MemorySegment:
    def __init__(self):
        self.index = defaultdict(PostingList)
        self._size_postings = 0 # number of bytes the postings in the index will occupy if packed. not incl. terms

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

    def add_token(self, term: str, doc_id: int, position: int):
        '''
        Adds a token to the index.
        A Token is a (term, doc_id, position) triplet, indicating that the term occurred in
        the document corresponding to doc_id at the given position.
        '''
        self.index[term].add_posting(Posting(doc_id, [position]))
        self._size_postings += 4 + 4

    def add_posting(self, term: str, posting: Posting):
        '''
        Adds a posting to the postings list of the given term. Convenience wrapper for PostingList.add_posting.
        :param term: str
        :param posting: Posting
        :return: None
        '''
        self.index[term].add_posting(posting)

        # not totally accurate size, but ok approximation
        self._size_postings += len(posting.positions)*4 + 4