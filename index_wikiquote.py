'''
Author: Andrew Chan
Contact: andrewkchan@berkeley.edu
License: MIT License
'''

import re
import bz2
from xml.etree.ElementTree import iterparse
from naive_dynamic_ix import index


def get_next_doc(xml_iter):
    '''
    Returns the next document in the given file.
    :param xml_iter: iterparse Iterator from xml.etree.ElementTree.iterparse
    :return: Dict with keys doc_title, doc_id, doc_body
    '''
    doc_lines = []
    while True:
        event, elem = xml_iter.__next__()
        if event == "start" and elem.tag[43:] == "page":
            break # start of a new page!

    doc_title, doc_body = None, None
    while True:
        event, elem = xml_iter.__next__()
        if event == "end" and elem.tag[43:] == "page":
            break
        elif event == "start" and elem.tag[43:] == "title":
            event, elem = xml_iter.__next__()
            doc_title = elem.text
        elif event == "start" and elem.tag[43:] == "text":
            event, elem = xml_iter.__next__()
            doc_body = elem.text
            #print(doc_body)

    if doc_title is None or doc_body is None:
        return None

    return {
        "doc_title": doc_title,
        "doc_id": doc_title,
        "doc_body": doc_body
    }


def index_collection(f):
    ix = index.Index("wikiquote.index", "wikiquote_docs.db")
    print("Started indexing...")
    xml_iter = iterparse(f, events=("start", "end"))
    doc = get_next_doc(xml_iter)
    counter = 0
    while doc:
        print("Indexed document" + str(counter) + ":" + doc["doc_title"])
        ix.add_document(**doc)
        doc = get_next_doc(xml_iter)
        counter += 1
    return ix

if __name__ == "__main__":
    with bz2.open("enwikiquote-20170801-pages-meta-current.xml.bz2") as f:
        ix = index_collection(f)
    print(ix.do_phrase_query(["Albert", "Einstein"]))
    print(ix.do_free_text_query(["people", "bomb"]))
    # print(sorted([k for k in ix.memory_segment.index.keys()]))