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

The reference implementation uses two libraries:

  - [beanstalkd](https://kr.github.io/beanstalkd/) for the queuing system.

  - [Django](https://www.djangoproject.com/) for the persistence layer,
    where the nodes and edges of the graph are stored in a relational model.

The way it works is that URLs _found_ are stored as records in a database table.
Not all URLs found are actually crawled, however; only pages with "Content-Type"
HTML will be loaded and crawled. The result is that all images, PDFs, etc are
terminal (ie, no outgoing links) by design.

The pseudo-code above is implemented in the `crawler_node.CrawlerNode` class.
The messages in the queue are (stringified) JSON objects. The pseudo-code
also requires access to a GraphAPI object with three methods:

  - the `is_visited`, `add_edge` methods query and update the graph;

  - the `adjacent_nodes` method needs to fetch a page, parse the HTML, and
    return all URLs linked to on the page.

The `webgraph.webgraph_api` module implements this concretely, with some
attention paid to separation of concerns. A "lower level" graph API in
`webgraph.models.API` encapsulates the logic needed for adding and querying
the nodes and edges implemented as tables, and the WebgraphAPI uses this.


## Running it

All commands to run the crawler handled through the `main.py` script. For
simplicity these instructions walk through running the crawler in distributed
mode on a single machine; for instance, the queue server running in one
terminal, and each crawler instance running in a separate terminal, all
communicating via `localhost`.

The `main.py` script does two basic things:

  - The `--seedfile` argument inserts a list of URLs (from a text file, one
    record per line) into the queue and exits. The seed URLs are nodes of
    depth 0 in the BFS algorithm.

  - The `--crawl` argument starts the BFS algorithm. Multiple processes
    can be run concurrently. The `max_depth` stopping criterion for BFS is
    set in `config.yaml`.

Before starting the main script, the Django app and the beanstalk server need
to be initialized.

### Python dependencies

Ensure the Python dependencies are installed; run pip in the project folder:

    $ sudo pip install -r requirements.txt

The Django version is pinned to 1.6; if you have a later version, this _may_
work, but has not been tested.

### Initializing Django app

_If you would like to test this with SQLite instead of MySQL, replace
the `DATABASE['default']` field in `settings.py` accordingly. However, SQLite
does not support concurrent access, so that this route prevents running
more than one crawler node at once._

To use the MySQL backend, create a Django user and database to match values in
`settings.py`; for instance, as the root user for MySQL:

    root> create database django;
    root> create user 'django' identified by '<YOUR PASSWORD>';
    root> grant all on django.* to 'django';

Update your chosen password in `settings.py`, and run the Django manager
from top level of the repo to create the new tables:

    $ ./manage.py syncdb

The [Django docs](https://docs.djangoproject.com/en/1.6/intro/tutorial01/)
give many more details.

### Running beanstalk

Install and launch [beanstalkd](https://kr.github.io/beanstalkd/)
in a terminal window.

The crawler app is configured to use the default host and port for beanstalk,
and these can by changed by editing the section in `config.yaml`


## License

BSD 2-clause.
