'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

import dbm

class DiskSegment:
    def __init__(self, gdbm):
        self._gdbm = gdbm

    @classmethod
    def from_file(cls, filename: str):
        '''
        Reads in an index file to create a new disk segment.
        :param filename: str - the filename of the existing index.
        :return: DiskSegment object.
        '''
        try:
            gdbm = dbm.gnu.open(filename, 'r') # read only!
            return cls(gdbm)
        except:
            raise FileNotFoundError("Bad disk segment file name")