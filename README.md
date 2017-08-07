[![Build Status](https://travis-ci.org/theandrewchan/search-engine-day-1.svg?branch=master)](https://travis-ci.org/theandrewchan/search-engine-day-1)

# search-engine-day-1

## naive-dynamic-ix

A hash-based inverted index. Uses Berkeley DB for backing disk segment, and a naive dynamic indexing scheme with a single auxiliary index 
in memory along with a single main index on disk. Supports one word and phrase queries.

Benchmarks are still WIP.
