[![Build Status](https://travis-ci.org/theandrewchan/search-engine-day-1.svg?branch=master)](https://travis-ci.org/theandrewchan/search-engine-day-1)

# search-engine-day-1

Day 1 of my own personal "Build a Search Engine in 5 days" challenge. Desiging the search engine is going to take a lot longer than 5
days; the end goal is to have something simple that I can explain so that others can build it within 5 days.

## naive-dynamic-ix

A hash-based inverted index. Uses Berkeley DB for backing disk segment, and a naive dynamic indexing scheme with a single auxiliary index 
in memory along with a single main index on disk. Supports one word and phrase queries.

Benchmarks are still WIP.
