'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

import bsddb3
from pickle import dumps, loads


class DocumentStore:
    def __init__(self, bsddb):
        self.repo = bsddb

    @classmethod
    def from_file(cls, filename: str):
        '''
        Reads in a repository file to create a new document store, or creates the file if it does not exist.
        :param filename: str - the filename of the index.
        :return: DocumentStore object.
        '''
        bsddb = bsddb3.hashopen(filename, 'c')
        return cls(bsddb)

    def has_key(self, doc_id):
        '''
        :param doc_id: The document id to search for in the repository
        :return: document is in the repository or not.
        '''
        return self.repo.has_key(dumps(doc_id))

    def keys(self):
        '''
        Supplies a generator over the keys in the document store repository.
        Note that all keys are pickled and must be loaded().
        :return: A generator over the repository's keys.
        '''
        return self.repo.keys()

    def add_document(self, doc_id, doc_title, doc_body):
        '''
        Stores a tuple (doc_title, doc_str) in the repository by document ID.
        :param doc_id: ID of the document
        :param doc_title: Title of the document
        :param doc_body: String content of the document
        :return:
        '''
        self.repo[dumps(doc_id)] = dumps((doc_title, doc_body))

    def get_document(self, doc_id):
        '''
        Returns a tuple (doc_title, doc_str) of the document given by doc_id,
        or raises a KeyError if the document is not in the repository.
        :param doc_id: ID of the document to retrieve.
        :return: (doc_title, doc_body)
        '''
        return loads(self.repo[dumps(doc_id)])
