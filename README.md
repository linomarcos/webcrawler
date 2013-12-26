The Simplest Webcrawler
-----------------------

A Breadth First Search algorith which crawls the Internet link graph.
The nodes and edges are stored in an SQLite database, for which the `Crawler`
class is an interface.

This is intended as a toy application: it a single-threaded BFS, and is _very_
network bound.

### Usage

Initialize a database using the commands in `config/schema.sql`, eg,

    $ mkdir data
    $ sqlite3 -init config/schema.sql data/testdb

and create a list of "seed" URLs, one per line, in a text file. Then

    $ python crawler.py data/testdb seed.txt

to start the crawler.

### License

BSD 2-clause.
