'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

from collections import defaultdict
from bisect import bisect_left
import gc


class Posting:
    def __init__(self, doc_id, positions: list):
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
        if position_i == len(self.positions) or self.positions[position_i] != position:
            self.positions.insert(position_i, position)

    @staticmethod
    def merge_postings(p1, p2):
        '''
        Merge the positions lists of the input postings into a new posting.
        '''
        if p1.doc_id != p2.doc_id:
            raise ValueError("Postings to merge do not have same doc id")
        i, j = 0, 0
        merged = []
        while i < len(p1.positions) or j < len(p2.positions):
            if i < len(p1.positions):
                if j < len(p2.positions):
                    if p1.positions[i] == p2.positions[j]:
                        merged.append(p1.positions[i])
                        i += 1
                        j += 1
                    elif p1.positions[i] < p2.positions[j]:
                        merged.append(p1.positions[i])
                        i += 1
                    else:
                        merged.append(p2.positions[j])
                        j += 1
                else:
                    merged.append(p1.positions[i])
                    i += 1
            else:
                merged.append(p2.positions[j])
                j += 1
        return Posting(p1.doc_id, merged)

    def __repr__(self):
        return "(" + repr(self.doc_id) + ":" + repr(self.positions) + ")"

    def __eq__(self, other):
        return self.positions == other.positions and self.doc_id == other.doc_id

    def __ne__(self, other):
        return not (self == other)


class PostingList:
    def __init__(self, postings = None):
        '''
        A PostingList maintains a list of Posting objects sorted by doc_id.
        '''
        self.postings = postings if postings else []

        # keep a separate list of doc ids mostly for convenience to use with bisect_left.
        self._doc_ids = [posting.doc_id for posting in self.postings]

    def add_posting(self, posting: Posting):
        '''
        Adds a posting to the posting list, maintaining sorted order by doc id.
        :param posting: Posting object
        :return: None
        '''
        posting_i = bisect_left(self._doc_ids, posting.doc_id)
        if posting_i == len(self._doc_ids) or self._doc_ids[posting_i] != posting.doc_id:
            # if we don't already have this doc in our postings list, insert it
            self.postings.insert(posting_i, posting)
            self._doc_ids.insert(posting_i, posting.doc_id)
        else:
            # if already have this doc, merge the positions lists of the postings
            self.postings[posting_i] = Posting.merge_postings(self.postings[posting_i], posting)

    def __repr__(self):
        return "< PostingList::" + repr(self.postings) + ";" + repr(self._doc_ids) + ">"

    @staticmethod
    def merge_lists(pl_1, pl_2):
        '''
        Merges 2 posting lists, returning a new posting list.
        For duplicate postings (with same doc id), merge the duplicates and append the merged posting.
        :param pl_1: PostingList
        :param pl_2: PostingList
        :return: Merged PostingList.
        '''
        i, j = 0, 0
        merged = []
        while i < len(pl_1.postings) or j < len(pl_2.postings):
            if i < len(pl_1.postings):
                if j < len(pl_2.postings):
                    if pl_1.postings[i].doc_id < pl_2.postings[j].doc_id:
                        merged.append(pl_1.postings[i])
                        i += 1
                    elif pl_1.postings[i].doc_id == pl_2.postings[j].doc_id:
                        merged.append(Posting.merge_postings(pl_1.postings[i], pl_2.postings[j]))
                        i += 1
                        j += 1
                    else:
                        merged.append(pl_2.postings[j])
                        j += 1
                else:
                    merged.append(pl_1.postings[i])
                    i += 1
            else:
                merged.append(pl_2.postings[j])
                j += 1
        return PostingList(merged)

    @staticmethod
    def find_phrases(posting_lists):
        '''
        Finds postings that recur throughout all the posting lists to form positional runs (phrases).
        For any given document id, a positional run is formed when a number of posting lists each contain
        that document id, and in sequential positions. Example:
        >>> x = PostingList([Posting(1, [2, 5]), Posting(2, [2])])
        >>> y = PostingList([Posting(1, [6])])
        >>> z = PostingList([Posting(1, [7]), Posting(2, [3])])
        >>> PostingList.find_phrases(iter([x, y, z]))
        >>>   PostingList([Posting(1, [5])])
        This is the basis for an "exact phrase" query. We can find the occurrence of the exact phrase "Peter Piper Pied"
        by finding positional runs for [PostingList("Peter"), PostingList("Piper"), PostingList("Pied")].
        :param posting_lists: Iterator where each element is a PostingList.
        :return: PostingList. The Postings contain start positions of found phrases.
        '''
        first_posting_list = posting_lists[0]
        # create forward index with doc_id as key and possible start positions of the phrase as values.
        fw_index = {posting.doc_id: set(posting.positions) for posting in first_posting_list.postings}
        doc_ids = set(fw_index.keys())

        for i, posting_list in enumerate(posting_lists[1:]):
            ith_doc_ids = set()
            for posting in posting_list.postings:
                doc_id = posting.doc_id
                ith_doc_ids.add(doc_id)
                if doc_id in fw_index:
                    # in a phrase, the ith term must occur i-1 spots after the 1st term.
                    # we start with the 2nd phrase as i=0, so subtract i+1
                    offset_poses = [pos-(i+1) for pos in posting.positions]
                    # discard possible phrase starts that don't coincide with any postings of the ith term.
                    fw_index[doc_id] &= set(offset_poses)
                    if len(fw_index[doc_id]) == 0:
                        fw_index.pop(doc_id, None)
            # discard doc ids where the ith phrase term does not occur
            bad_doc_ids = doc_ids - ith_doc_ids
            for doc_id in bad_doc_ids:
                fw_index.pop(doc_id, None)

        # any non-empty entries in the dictionary indicate documents where the phrase occurs.
        result_postings = [Posting(item[0], sorted(item[1])) for item in fw_index.items()]
        return PostingList(result_postings)

class MemorySegment:
    def __init__(self):
        self.index = defaultdict(PostingList)
        self._size_postings = 0 # number of bytes the postings in the index will occupy if packed. not incl. terms

    def get_size(self):
        '''
        :return: Size in bytes of index's postings.
        '''
        return self._size_postings

    def do_one_word_query(self, term: str) -> list:
        '''
        Executes a one word query on the index with the given term.
        :param term: str
        :return: List of matching doc ids.
        '''
        posting_list = self.index[term]
        doc_ids = [posting.doc_id for posting in posting_list.postings]
        return doc_ids

    def do_phrase_query(self, terms: list) -> list:
        '''
        Executes a phrase query on the index with the given sequence of terms.
        :param terms: List of strings representing the exact phrase in order.
        :return: List of matching doc ids.
        '''
        term_postlists = [self.index[term] for term in terms]
        phrase_postings = PostingList.find_phrases(term_postlists).postings
        doc_ids = [posting.doc_id for posting in phrase_postings]
        return doc_ids

    def add_token(self, term: str, doc_id, position: int):
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

    def merge_into_disk(self, disk_segment):
        '''
        Merges this memory segment into the given disk segment.
        :param disk_segment: DiskSegment
        :return: None
        '''
        for term in self.index.keys():
            disk_segment.merge_posting_list(term, self.index[term])

    def clear(self):
        '''
        Clears all data in the memory segment.
        :return: None
        '''
        # don't use dict.clear because the underlying hash table stays the same size
        self.index = defaultdict(PostingList)
        gc.collect()
