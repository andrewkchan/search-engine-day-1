'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

from naive_dynamic_ix.memory_segment import MemorySegment
from naive_dynamic_ix.disk_segment import DiskSegment


class Index:
    '''
    Global index with underlying main index on disk and auxiliary index in memory.
    '''
    def __init__(self):
        self.disk_segment = DiskSegment.from_file("index.db")
        self.memory_segment = MemorySegment()

    def add_document(self, document):
        # TODO
        pass