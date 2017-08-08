import unittest
import os

from naive_dynamic_ix.disk_segment import DiskSegment
from naive_dynamic_ix.memory_segment import Posting, PostingList
from pickle import loads

class TestDiskSegment(unittest.TestCase):
    def setUp(self):
        if os.path.isfile("test_ix.db"):
            os.remove("test_ix.db")
        self.disk_ix = DiskSegment.from_file("test_ix.db")

    def test_merge_and_queries(self):
        p1 = Posting("bus.com", [0, 1])
        p2 = Posting("car.com", [3, 4])
        p3 = Posting("truck.com", [5, 6])
        p4 = Posting("van.com", [7, 8])
        plist1 = PostingList([p1, p3])
        plist2 = PostingList([p2, p4])

        self.disk_ix.merge_posting_list("vehicle", plist1)

        res = self.disk_ix.do_one_word_query("vehicle")
        self.assertEqual(res, ["bus.com", "truck.com"])

        self.disk_ix.merge_posting_list("vehicle", plist2)

        res = self.disk_ix.do_one_word_query("vehicle")
        self.assertEqual(res, ["bus.com", "car.com", "truck.com", "van.com"])

        self.disk_ix.merge_posting_list("bus", PostingList([p1]))
        self.disk_ix.merge_posting_list("car", PostingList([p2]))
        self.disk_ix.merge_posting_list("truck", PostingList([p3]))
        self.disk_ix.merge_posting_list("van", PostingList([p4]))

        res = self.disk_ix.do_one_word_query("bus")
        self.assertEqual(res, ["bus.com"])

        keys = set(loads(k) for k in self.disk_ix.keys())
        self.assertIn("bus", keys)
        self.assertIn("car", keys)
        self.assertIn("truck", keys)
        self.assertIn("van", keys)

        empty_res = self.disk_ix.do_one_word_query("plane")
        self.assertEqual(empty_res, [])

        # winter
        p1_0 = Posting("hbo.com", [0, 5])
        p1_1 = Posting("disney.com", [1, 4])
        p1_2 = Posting("patagonia.com", [2])
        self.disk_ix.merge_posting_list("winter", PostingList([p1_0, p1_1, p1_2]))

        # is
        p2_0 = Posting("hbo.com", [1])
        p2_1 = Posting("wikipedia.org", [3, 10])
        p2_2 = Posting("patagonia.com", [5])
        self.disk_ix.merge_posting_list("is", PostingList([p2_0, p2_1, p2_2]))

        # coming
        p3_0 = Posting("hbo.com", [2, 4])
        p3_1 = Posting("patagonia.com", [4])
        self.disk_ix.merge_posting_list("coming", PostingList([p3_0, p3_1]))

        pq_result = self.disk_ix.do_phrase_query(["winter", "is", "coming"])
        self.assertEqual(pq_result, ["hbo.com"])
        pq_empty_result = self.disk_ix.do_phrase_query(["coming", "is", "winter"])
        self.assertEqual(pq_empty_result, [])

    def tearDown(self):
        os.remove("test_ix.db")