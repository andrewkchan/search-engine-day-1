import unittest

from naive_dynamic_ix.memory_segment import Posting, PostingList, MemorySegment


class TestPosting(unittest.TestCase):
    def test_add_position(self):
        p = Posting("wiki", [1, 2, 4])
        p.add_position(3)
        self.assertEqual(p.positions, [1, 2, 3, 4])
        p.add_position(5)
        self.assertEqual(p.positions, [1, 2, 3, 4, 5])

    def test_merge_posting(self):
        p = Posting("dumdumdum", [1, 3, 4])
        p2 = Posting("dumdumdum", [2, 5, 6])
        p.merge_posting(p2)
        self.assertEqual(p.positions, [1, 2, 3, 4, 5, 6])
        self.assertEqual(p2.positions, [2, 5, 6])

class TestPostingList(unittest.TestCase):
    def test_add_posting(self):
        plist = PostingList()
        p = Posting("dog.com", [1,2,3])
        plist.add_posting(p)
        self.assertEqual(plist.postings, [p])
        self.assertEqual(plist._doc_ids, ["dog.com"])
        p2 = Posting("cat.com", [2,5,9])
        plist.add_posting(p2)
        self.assertEqual(plist.postings, [p2, p])
        self.assertEqual(plist._doc_ids, ["cat.com", "dog.com"])
        p3 = Posting("chimp.net", [5,6])
        plist.add_posting(p3)
        self.assertEqual(plist.postings, [p2, p3, p])
        self.assertEqual(plist._doc_ids, ["cat.com", "chimp.net", "dog.com"])
        p4 = Posting("chimp.net", [9,10])
        plist.add_posting(p4) # will merge existing doc id
        self.assertEqual(plist.postings, [p2, p3, p])
        self.assertEqual(p3.positions, [5,6,9,10]) # merge will modify original posting

    def test_merge_lists(self):
        p1 = Posting("bus.com", [0,1])
        p2 = Posting("car.com", [3,4])
        p3 = Posting("truck.com", [5,6])
        p4 = Posting("van.com", [7,8])
        plist1 = PostingList([p1, p3])
        plist2 = PostingList([p2, p4])
        merged_plist = PostingList.merge_lists(plist1, plist2)
        self.assertEqual(merged_plist.postings, [p1, p2, p3, p4])
        self.assertEqual(merged_plist._doc_ids, ["bus.com", "car.com", "truck.com", "van.com"])
        # duplicate posting doc id
        p1_1 = Posting("bus.com", [2])
        merged_plist = PostingList.merge_lists(merged_plist, PostingList([p1_1]))
        self.assertEqual(merged_plist._doc_ids, ["bus.com", "car.com", "truck.com", "van.com"])
        self.assertEqual(merged_plist.postings[0].positions, [0,1,2])

    def test_find_phrases(self):
        # winter
        p1_0 = Posting("hbo.com", [0,5])
        p1_1 = Posting("disney.com", [1,4])
        p1_2 = Posting("patagonia.com", [2])

        # is
        p2_0 = Posting("hbo.com", [1])
        p2_1 = Posting("wikipedia.org", [3, 10])

        # coming
        p3_0 = Posting("hbo.com", [2,4])
        p3_1 = Posting("patagonia.com", [4])

        plist1 = PostingList([p1_0, p1_1, p1_2])
        plist2 = PostingList([p2_0, p2_1])
        plist3 = PostingList([p3_0, p3_1])
        phrase_plist = PostingList.find_phrases(iter([plist1, plist2, plist3]))
        self.assertEqual(phrase_plist.postings[0].doc_id, "hbo.com")
        self.assertEqual(phrase_plist.postings[0].positions, [0])

class TestMemorySegment(unittest.TestCase):
    def test_add_posting_and_clear(self):
        ix = MemorySegment()
        p1 = Posting("bus.com", [0, 1])
        p2 = Posting("car.com", [3, 4])
        p3 = Posting("truck.com", [5, 6])
        p4 = Posting("van.com", [7, 8])
        ix.add_posting("vehicle", p1)
        ix.add_posting("vehicle", p3)
        ix.add_posting("vehicle", p2)
        ix.add_posting("vehicle", p4)
        self.assertEqual(ix.index["vehicle"].postings, [p1, p2, p3, p4])

        ix.clear()
        self.assertEqual(len(ix.index.items()), 0)

    def test_queries(self):
        ix = MemorySegment()
        # winter
        p1_0 = Posting("hbo.com", [0, 5])
        p1_1 = Posting("disney.com", [1, 4])
        p1_2 = Posting("patagonia.com", [2])
        ix.add_posting("winter", p1_0)
        ix.add_posting("winter", p1_1)
        ix.add_posting("winter", p1_2)

        # is
        p2_0 = Posting("hbo.com", [1])
        p2_1 = Posting("wikipedia.org", [3, 10])
        p2_2 = Posting("patagonia.com", [5])
        ix.add_posting("is", p2_0)
        ix.add_posting("is", p2_1)
        ix.add_posting("is", p2_2)

        # coming
        p3_0 = Posting("hbo.com", [2, 4])
        p3_1 = Posting("patagonia.com", [4])
        ix.add_posting("coming", p3_0)
        ix.add_posting("coming", p3_1)

        # one word query
        owq_result = ix.do_one_word_query("winter")
        self.assertEqual(owq_result.doc_ids, ["disney.com", "hbo.com", "patagonia.com"])
        owq_empty_result = ix.do_one_word_query("frozen")
        self.assertEqual(owq_empty_result.doc_ids, [])
        # phrase query
        pq_result = ix.do_phrase_query(["winter", "is", "coming"])
        self.assertEqual(pq_result.doc_ids, ["hbo.com"])
        pq_empty_result = ix.do_phrase_query(["coming", "is", "winter"])
        self.assertEqual(pq_empty_result.doc_ids, [])
        ix.clear()




if __name__ == "__main__":
    unittest.main()