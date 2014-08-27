Simple Distributed Webcrawler
-----------------------------

In theory, crawling a subset of the web link graph is a straightforward
application of breadth-first search. A queue structure is initialized with
a set of seed URLS (or "nodes"); nodes are popped off the queue and processed
in turn, with links on those pages being added to the queue, until a specified
search depth is reached. In this way the link graph structure is assembled by
discovery. Modulo the logic needed needed for fetching pages and parsing links,
the entire algorithm can be implemented in a couple dozen lines of Python.

The theory is easy. In practice, implementing classical -- that is, single-process
-- breadth-first search will be _very_ network bound. Visiting each node entails
resolving and fetching a page from the Internet, and about 99% of the CPU time
will be spent waiting on this.

This project is a toy model of a distributed crawler.

Fetching a single page and extracting its outbound links can be handled
independently of the other pages in the link graph, so that this task can be
assigned to several concurrent "workers." Overall the process remains network
bound, but one can expect a linear speed-up in the number of worker
processes deployed -- that is, at least, until network bandwidth is saturated.

## Design

Even if most of the work is handled by identical concurrent processes, BFS
requires two central components:

1. a shared queue that all workers read from and push new work to,
2. a shared data structure that represents the link graph, and which maintains
a list of nodes visited (to prevent repeatedly traversing cycles in the graph).

The variant of the BFS algorithm here uses as a stopping condition a `MAX_DEPTH`
for the edge distance traversed from the set of starting nodes. The accounting
is handled by pairing each item of work with its search depth. In the pseudo-code
below, these are represented by the `.url` and the `.depth` members of the
`TaskParams` object, respectively:

    while not Queue.is_empty():
        task_params = Queue.pop()
        if task_params.depth > MAX_DEPTH or GraphAPI.is_visited(task_params.url):
            continue
        for new_url in GraphAPI.adjacent_nodes(task_params.url):
            GraphAPI.add_edge(task_params.url, new_url)
            Queue.put(TaskParams(url=new_url, depth=task_params.depth+1))

In particular, the search depth is defined recursively; all starting nodes
have depth zero by definition.

The graph data structure is assembled in the "data layer." As illustrated in the
pseudo-code above, there are only a few points of contact with the BFS algorithm,
each of these being a call to a method of the prototype `GraphAPI`.


## Implementation

Write this up.

## Dependencies

For the shared queue we use [beanstalkd](https://kr.github.io/beanstalkd/),
and [beanstalkc](https://github.com/earl/beanstalkc/) for the Python client.
As mentioned above, the graph is represented via a relational model, and
[Django](https://www.djangoproject.com/) is used for this.


### License

BSD 2-clause.
