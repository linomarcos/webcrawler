import re
import logging
import requests
from requests.exceptions import RequestException
from sqlite3 import connect as sqlite_conn
from sqlite3 import IntegrityError
from ssl import SSLError
from bs4 import BeautifulSoup
from urlparse import urlparse, urlunparse
from collections import deque


def clean_url(url):
    scheme, netloc, path, _, _, _ = urlparse(url)
    return urlunparse((scheme, netloc, path, None, None, None))

def get_links(base_url, raw_html):
    """
    Returns the set of URLs from the body element of HTML.

    @param base_url [str]: for page being parsed,
    @param raw_html [str]: for page being parsed
    @return
    """
    base_scheme, base_netloc, _, _, _, _ = urlparse(base_url)
    parsed = BeautifulSoup(raw_html)
    links = set()
    if not parsed.body:
        return links
    is_http_link = re.compile(r'^http')
    for link in parsed.body.find_all('a'):
        scheme, netloc, path, _, _, _, = urlparse(link.get('href', ''))
        if scheme and not is_http_link.match(scheme):
            continue
        if scheme and netloc:  # full link as href
            links.add(urlunparse((scheme, netloc, path, None, None, None)))
        elif path:  # relative link as href
            links.add(urlunparse((base_scheme, base_netloc, path, None, None, None)))

    return links


class Crawler(object):
    TIMEOUT = 5  # seconds

    """
    Basic web-graph crawler: fetches pages and persists the link-graph structure
    of their URLS in a relational database.
    """
    def __init__(self, sqlitedb):
        self.conn = sqlite_conn(sqlitedb)
        self.conn.isolation_level = None
        # <http://www.sqlite.org/foreignkeys.html#fk_enable>
        cursor = self.conn.cursor()
        cursor.execute('PRAGMA foreign_keys = ON')
        logging.info('Connected to %s', sqlitedb)

    def get_node_id(self, url):
        """
        Maintains 'URL -> id' map. Inserts a node in the table if not present.

        @param url [str]
        @return id [int]
        """
        cursor = self.conn.cursor()
        cursor.execute('select id from nodes where url=?', (url,))
        record = cursor.fetchone()
        if not record:
            cursor.execute('insert into nodes (url) values (?)', (url,))
            cursor.execute('select id from nodes where url=?', (url,))
            record = cursor.fetchone()
        (node_id,) = record
        return node_id

    def add_edge(self, tail_id, head_id):
        """
        Adds an edge 'tail -> head' to the table.

        @param tail_id, head_id [int]: values from L{get_node_id} method.
        """
        cursor = self.conn.cursor()
        try:
            cursor.execute('insert into edges (head_id, tail_id) values (?, ?)',
                           (head_id, tail_id))
        except IntegrityError, ie:
            logging.debug('%s (%d, %d)', ie, tail_id, head_id)

    def is_marked(self, node_id):
        """
        @param node_id [int]
        @return [bool]: 'is_visited is not NULL' for corresponding node id.
        """
        cursor = self.conn.cursor()
        cursor.execute('select is_visited from nodes where id=?', (node_id,))
        record = cursor.fetchone() or (None,)
        return (record[0] is not None)

    def do_mark(self, node_id, value):
        """
        Updates the 'is_visited' field for the node id with the (string) value.
        """
        cursor = self.conn.cursor()
        cursor.execute('update nodes set is_visited=? where id=?',
                       (str(value), node_id))

    def fetch(self, seed_list, max_depth=2):
        queue = deque([(clean_url(url), 0) for url in seed_list])
        while len(queue) > 0:
            (url, depth) = queue.popleft()
            url_id = self.get_node_id(url)
            if self.is_marked(url_id) or (depth > max_depth):
                continue
            self.do_mark(url_id, depth)
            try:
                resp = requests.get(url, timeout=self.TIMEOUT)
                if not resp.ok:
                    continue
                for outlink in get_links(url, resp.text):
                    out_id = self.get_node_id(outlink)
                    self.add_edge(url_id, out_id)
                    queue.append((outlink, depth + 1))
            except (RequestException, SSLError), ex:
                logging.info('%s %s', url, ex)


USAGE ="""
./crawler.py <sqlitedb> <seed_list> [max_depth]

- sqlitedb    file name of initialized SQLite database
- seed_list   file name of initial URLs, one per line
- max_depth   number of levels to extend breadth-first-search. [default=2]
"""

LOGGING_CONFIG = {
    'format': '%(asctime)s %(levelname)s  %(message)s',
    'level': logging.INFO,
}

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print USAGE
        sys.exit(0)

    logging.basicConfig(**LOGGING_CONFIG)

    logging.info('reading list from %s', sys.argv[2])
    seed_list = [line.strip() for line in open(sys.argv[2])]

    max_depth = 2
    if len(sys.argv) > 3:
        max_depth = int(sys.argv[3])
        logging.info('using max_depth %d', max_depth)

    crawler = Crawler(sys.argv[1])
    crawler.fetch(seed_list, max_depth)

