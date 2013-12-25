import logging
import requests
from sqlite3 import connect as sqlite_conn
from sqlite3 import IntegrityError
from bs4 import BeautifulSoup
from urlparse import urlparse, urlunparse


def clean_url(url):
    pass

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
    for link in parsed.body.find_all('a'):
        scheme, netloc, path, _, _, _, = urlparse(link.get('href', ''))
        if scheme and netloc:
            links.add(urlunparse((scheme, netloc, path, None, None, None)))
        elif path:
            links.add(urlunparse((base_scheme, base_netloc, path, None, None, None)))

    return links


class Crawler(object):
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
        pass

    def do_mark(self, node_id, value):
        pass

    def fetch(self, seed_list):
        pass

