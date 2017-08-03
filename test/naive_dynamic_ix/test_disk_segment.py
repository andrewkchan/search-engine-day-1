import unittest

from naive_dynamic_ix.disk_segment import DiskSegment
from naive_dynamic_ix.memory_segment import Posting, PostingList

class TestDiskSegment(unittest.TestCase):
    def test_merge_and_queries(self):
        p1 = Posting("bus.com", [0, 1])
        p2 = Posting("car.com", [3, 4])
        p3 = Posting("truck.com", [5, 6])
        p4 = Posting("van.com", [7, 8])
        plist1 = PostingList([p1, p3])
        plist2 = PostingList([p2, p4])

        disk_ix = DiskSegment.from_file("test_ix.db")
        disk_ix.merge_posting_list("vehicle", plist1)

        res = disk_ix.do_one_word_query("vehicle")
        self.assertEqual(res.doc_ids, ["bus.com", "truck.com"])

        disk_ix.merge_posting_list("vehicle", plist2)

        res = disk_ix.do_one_word_query("vehicle")
        self.assertEqual(res.doc_ids, ["bus.com", "car.com", "truck.com", "van.com"])

        disk_ix.merge_posting_list("bus", PostingList([p1]))
        disk_ix.merge_posting_list("car", PostingList([p2]))
        disk_ix.merge_posting_list("truck", PostingList([p3]))
        disk_ix.merge_posting_list("van", PostingList([p4]))

        res = disk_ix.do_one_word_query("bus")
        self.assertEqual(res.doc_ids, ["bus.com"])

        keys = set(k for k in disk_ix.keys())
        self.assertIn("bus", keys)
        self.assertIn("car", keys)
        self.assertIn("truck", keys)
        self.assertIn("van", keys)

        empty_res = disk_ix.do_one_word_query("plane")
        self.assertEquals(empty_res.doc_ids, [])

        # winter
        p1_0 = Posting("hbo.com", [0, 5])
        p1_1 = Posting("disney.com", [1, 4])
        p1_2 = Posting("patagonia.com", [2])
        disk_ix.add_posting("winter", p1_0)
        disk_ix.add_posting("winter", p1_1)
        disk_ix.add_posting("winter", p1_2)

        # is
        p2_0 = Posting("hbo.com", [1])
        p2_1 = Posting("wikipedia.org", [3, 10])
        p2_2 = Posting("patagonia.com", [5])
        disk_ix.add_posting("is", p2_0)
        disk_ix.add_posting("is", p2_1)
        disk_ix.add_posting("is", p2_2)

        # coming
        p3_0 = Posting("hbo.com", [2, 4])
        p3_1 = Posting("patagonia.com", [4])
        disk_ix.add_posting("coming", p3_0)
        disk_ix.add_posting("coming", p3_1)

        pq_result = disk_ix.do_phrase_query(["winter", "is", "coming"])
        self.assertEqual(pq_result.doc_ids, ["hbo.com"])
        pq_empty_result = disk_ix.do_phrase_query(["coming", "is", "winter"])
        self.assertEqual(pq_empty_result.doc_ids, [])