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
    def __init__(self, doc_ids = [], doc_titles = [], snippets = []):
        # the following should be parallel lists.
        self.doc_ids = doc_ids
        self.doc_titles = doc_titles
        self.snippets = snippets

    def __str__(self):
        return "(" + ",".join(
            [(self.doc_ids[i], self.doc_titles[i], self.snippets[i]) for i in range(0, len(self.doc_ids))]
        ) + ")"
