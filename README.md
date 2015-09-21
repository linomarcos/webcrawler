Simple Distributed Webcrawler
-----------------------------

In theory, crawling a subset of the web link graph is a straightforward
application of breadth-first search. A queue structure is initialized with
a set of seed URLS (or "nodes"); nodes are popped off the queue and processed
in turn, with links on those pages being added to the queue, until a specified
search depth is reached. In this way the link graph structure is assembled by
discovery. Modulo the logic needed needed for fetching pages and parsing links,
the entire algorithm can be implemented in a couple dozen lines of Python.

The theory is easy. In practice, implementing classical -- that is,
single-process -- breadth-first search will be _very_ network bound. Visiting
each node entails resolving and fetching a page from the Internet, and about
99% of the CPU time will be spent waiting on this.

This project is a toy model of a distributed crawler.

Fetching a single page and extracting its outbound links can be handled
independently of the other pages, so that this task can be assigned to several
concurrent "workers." Overall the process remains network bound, but one can
expect a linear speed-up in the number of worker processes deployed -- that is,
at least, until network bandwidth is saturated.

## Design

Even if most of the work is handled by concurrent processes, BFS requires
the following central components:

  1. a shared queue that all workers read from and push new work to,
  2. a shared data structure maintaining the list of all nodes visited, to
     prevent traversing the same node repeatedly,
  3. a shared data structure to represent the link graph

The algorithm here uses as a stopping condition a "max depth" value for the
edge distance traversed from the set of starting nodes. The accounting is
handled by pairing each item of work with its search depth. In the pseudo-code
below, these are represented by the `.url` and the `.depth` members of the
`Task` object, respectively:

    while not Queue.is_empty():
        task = Queue.pop()
        if task.depth > MAX_DEPTH or VisitSet.contains(task.url):
            continue
        VisitSet.add(task.url)
        for new_url in GraphAPI.adjacent_nodes(task.url):
            Queue.put(Task(url=new_url, depth=task.depth+1))

The `GraphAPI` object needs a bit of explanation. Its one exposed method,
`adjacent_nodes` processes a task, ie, fetches a page, and returns the set
of new jobs that need to be handled. In the process it records the new edges
of the link graph discovered.


## Implementation

A relational database is used for representing the link graph. For this the
[Django](https://www.djangoproject.com/) ORM is used, and the data model is
expressed in the `webgraph.models` module.

The queuing system and "visit set" is implemented in [Redis](http://redis.io/).


## License

BSD 2-clause.
