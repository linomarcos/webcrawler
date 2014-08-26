import re
import logging
import requests
from bs4 import BeautifulSoup
from urlparse import urlsplit, urlunsplit
from collections import deque

requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.WARN)

def get_clean_url(target_url, base_url=None):
    """Strips all query parameters and fragements from `target_url`, and tries
    to convert relative paths to absolute if `base_url` is provided.
    """
    cleaned = None
    scheme, netloc, path, _, _ = urlsplit(target_url)
    # ignore non-HTTP links
    if scheme and not re.match(r'^http', scheme):
        return None
    # prefer absolute paths
    if scheme and netloc:
        cleaned = urlunsplit((scheme, netloc, path, None, None))
    # otherwise try to create an absolute path
    if base_url and path:
        base_scheme, base_netloc, _, _, _ = urlsplit(base_url)
        cleaned = urlunsplit((base_scheme, base_netloc, path, None, None))

    return cleaned

def get_outbound_urls(src_url, timeout=4):
    """Returns the set of (absolute) outbound urls from a source document.
    """
    outbound_urls = set()
    try:
        head = requests.head(src_url, timeout=timeout)
        if (head.status_code != 200 or
            head.headers.get('content-type').find('html') == -1):
            return []
        logging.info('fetching %s', src_url)
        resp = requests.get(src_url, timeout=timeout)
        parsed = BeautifulSoup(resp.text)
        if not parsed.body:
            return []
        for link in parsed.body.find_all('a'):
            if not link.get('href'):
                continue
            target_url = get_clean_url(link.get('href'), src_url)
            if target_url:
                outbound_urls.add(target_url)
    except Exception as ex:
        logging.warning('[%s] %s', src_url, ex)

    return list(outbound_urls)


class Crawler(object):
    """Basic web-graph crawler: fetches pages and assembles the link graph.
    """
    def __init__(self):
        self._index = {}
        self._edges = []

    def _get_index(self, url):
        """Returns the index of the node in the adjacency representation.
        If the node is not present, an entry is added to the index and an
        entry is allocated for its adjacent edges.
        """
        if url not in self._index:
            self._index[url] = len(self._index)
            self._edges.append(None)
        return self._index[url]

    def crawl(self, seed_list, max_depth=2):
        queue = deque([(url, 0) for url in seed_list])
        while len(queue) > 0:
            (url, depth) = queue.popleft()
            if (depth > max_depth) or (self.is_visited(url)):
                continue
            outbound_urls = get_outbound_urls(url)
            index = self._get_index(url)
            self._edges[index] = map(self._get_index, outbound_urls)
            for url in outbound_urls:
                queue.append((url, depth+1))

    def is_visited(self, url):
        if url not in self._index:
            return False
        return (self._edges[self._get_index(url)] is not None)


USAGE ="""
./crawler.py <seed_list> [max_depth]

- seed_list   file name of initial URLs, one per line
- max_depth   number of levels to extend breadth-first-search. [default=2]
"""

LOGGING_CONFIG = {
    'format': '%(asctime)s %(levelname)s  %(message)s',
    'level': logging.INFO,
}

if __name__ == '__main__':
    import sys
    import json

    if len(sys.argv) < 2:
        print USAGE
        sys.exit(0)

    logging.basicConfig(**LOGGING_CONFIG)

    logging.info('reading list from %s', sys.argv[1])
    seed_list = [line.strip() for line in open(sys.argv[1])]

    max_depth = 2
    if len(sys.argv) > 2:
        max_depth = int(sys.argv[2])
        logging.info('using max_depth %d', max_depth)

    crawler = Crawler()
    crawler.crawl(seed_list, max_depth)

    filename = '%s.crawled.json' % sys.argv[1]
    logging.info('writing %d nodes to %s', len(crawler._index), filename)
    with open(filename, 'w') as fh:
        representation = dict(index=crawler._index, edges=crawler._edges)
        json.dump(representation, fh, indent=2)
        fh.write('\n')
