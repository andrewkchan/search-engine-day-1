'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

class Results:
    '''
    High-level object representing the results of a given query.
    Includes information about the documents containing the query as well as
    the snippets of those documents where the query occurs.
    '''
    def __init__(self, doc_ids = [], snippets = []):
        # the following should be parallel lists.
        self.doc_ids = doc_ids
        self.snippets = snippets