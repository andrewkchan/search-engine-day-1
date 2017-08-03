'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

import bsddb3
from pickle import dumps, loads
from naive_dynamic_ix.memory_segment import PostingList
from naive_dynamic_ix.results import Results


class DiskPostingListIterator:
    '''
    Iterator that yields the posting lists for a given list of terms and a disk segment to process queries.
    '''
    def __init__(self, disk_segment, terms):
        '''
        Creates an iterator that yields the posting lists (in order) for a given list of terms
        and a disk segment to process the queries for the terms.
        :param disk_segment: DiskSegment object.
        :param terms: list of string terms.
        '''
        self.disk_segment = disk_segment
        self.terms = terms

    def __iter__(self):
        self.i = 0
        return self

    def __next__(self):
        if self.i > len(self.terms):
            raise StopIteration
        term = self.terms[self.i]
        self.i += 1
        try:
            term_pl = loads(self.disk_segment.index[dumps(term)])
            return term_pl
        except KeyError:
            return PostingList()


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
        try:
            posting_list = loads(self.index[dumps(term)])
            print(posting_list)
            doc_ids = [posting.doc_id for posting in posting_list.postings]
            return Results(doc_ids)
        except KeyError:
            return Results([])

    def do_phrase_query(self, terms: list) -> Results:
        '''
        Executes a phrase query on the index with the given sequence of terms.
        :param terms: List of strings representing the exact phrase in order.
        :return: Results object with doc ids but not results snippets.
        '''
        posting_lists = DiskPostingListIterator(self, terms)
        result_pl = PostingList.find_phrases(posting_lists)
        doc_ids = [posting.doc_id for posting in result_pl.postings]
        return Results(doc_ids)

    def has_key(self, term: str):
        '''
        :param term:
        :return: term is in the index or not.
        '''
        return self.index.has_key(dumps(term))

    def keys(self):
        '''
        Supplies a generator over the keys in the disk segment.
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
            print(merged_pl)
            self.index[dumps(term)] = dumps(merged_pl)
        else:
            self.index[dumps(term)] = dumps(posting_list)