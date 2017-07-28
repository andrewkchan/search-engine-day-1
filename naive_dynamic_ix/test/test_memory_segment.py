import unittest

from naive_dynamic_ix.memory_segment import Posting, PostingList, MemorySegment


class TestPosting(unittest.TestCase):
    def test_add_position(self):
        p = Posting("wiki", [1, 2, 4])
        p.add_position(3)
        self.assertEqual(p.positions, [1, 2, 3, 4])
        p.add_position(5)
        self.assertEqual(p.positions, [1, 2, 3, 4, 5])

        p = Posting("stuff")
        p.add_position(0)
        self.assertEqual(p.positions, [0])

    def test_merge_posting(self):
        p = Posting("dumdumdum", [1, 3, 4])
        p2 = Posting("dumdumdum", [2, 5, 6])
        p.merge_posting(p2)
        self.assertEqual(p.positions, [1, 2, 3, 4, 5, 6])
        self.assertEqual(p2.positions, [2, 5, 6])

class TestPostingList(unittest.TestCase):
    def test_add_posting(self):
        plist = PostingList()
        p = Posting("dog", [1,2,3])
        plist.add_posting(p)
        self.assertEqual(plist.postings, [p])
        self.assertEqual(plist._doc_ids, ["dog"])
        p2 = Posting("cat", [2,5,9])
        plist.add_posting(p2)
        self.assertEqual(plist.postings, [p2, p])
        self.assertEqual(plist._doc_ids, ["cat", "dog"])
        p3 = Posting("chimp", [5,6])
        plist.add_posting(p3)
        self.assertEqual(plist.postings, [p2, p3, p])
        self.assertEqual(plist._doc_ids, ["cat", "chimp", "dog"])
        p4 = Posting("chimp", [9,10])
        plist.add_posting(p4) # will merge existing doc id
        self.assertEqual(plist.postings, [p2, p3, p])
        self.assertEqual(p3.positions, [5,6,9,10]) # merge will modify original posting

    def test_merge_lists(self):
        p1 = Posting("bus", [0,1])
        p2 = Posting("car", [3,4])
        p3 = Posting("truck", [5,6])
        p4 = Posting("van", [7,8])
        plist1 = PostingList([p1, p3])
        plist2 = PostingList([p2, p4])
        merged_plist = PostingList.merge_lists(plist1, plist2)
        self.assertEqual(merged_plist.postings, [p1, p2, p3, p4])
        self.assertEqual(merged_plist._doc_ids, ["bus", "car", "truck", "van"])

    def test_find_phrases(self):
        p1 = Posting("winter", [0,5])
        p2 = Posting("is", [1])
        p3 = Posting("coming", [2,4])
        plist = PostingList([p1, p2, p3])
        phrase_plist = PostingList.find_phrases(iter([p1, p2, p3]))
        self.assertEqual(phrase_plist.postings[0].doc_id, "coming")
        self.assertEqual(phrase_plist.postings[1].doc_id, "is")
        self.assertEqual(phrase_plist.postings[2].doc_id, "winter")
        self.assertEqual(phrase_plist.postings[0].positions, [2])
        self.assertEqual(phrase_plist.postings[1].positions, [1])
        self.assertEqual(phrase_plist.postings[2].positions, [0])

class TestMemorySegment(unittest.TestCase):
    pass

if __name__ == "__main__":
    unittest.main()