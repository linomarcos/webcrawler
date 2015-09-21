import os
import logging
import requests
import urlparse
from bs4 import BeautifulSoup
from webgraph.models import add_edge


logging.getLogger('requests').setLevel(logging.WARN)

def load_html(url, timeout=2):
    """Returns the parsed HTML or `None` if the page cannot be loaded."""
    try:
        resp = requests.head(url, timeout=timeout)
        resp.raise_for_status()

        content_type = resp.headers.get('content-type')
        if (content_type or '').lower().find('html') == -1:
            raise Exception('content-type: %s', resp.headers)

        logging.info('fetching %s', url)
        resp = requests.get(url, timeout=timeout)
        return BeautifulSoup(resp.text, 'html.parser')

    except Exception as ex:
        logging.warning('%s: %s', url, ex)
        return None

def clean_url(srcurl, href):
    """Returns the absolute path from a source page and HREF attribute,
    stripping any query params and fragments.
    """
    scheme, netloc, path, _, _ = urlparse.urlsplit(href)
    if scheme and not scheme.startswith('http'):
        return None

    if scheme and netloc:
        return urlparse.urlunsplit((scheme, netloc, path, None, None))

    srcscheme, srcloc, _, _, _ = urlparse.urlsplit(srcurl)
    return urlparse.urlunsplit((srcscheme, srcloc, path, None, None))


class WebGraphAPI(object):
    """Interface to data layer for MVP webgraph crawler.

    The main method exposed is @adjacent_nodes, which reads in a "task" from
    the CrawlerNode, and emits a list of new tasks.
    """

    def adjacent_nodes(self, url):
        """Returns a list of all out-links from the URL"""

        html = load_html(url)
        if not html or not html.body:
            return []

        hrefs = filter(None, [elem.get('href') for elem in html.body.find_all('a')])
        desturls = filter(None, [clean_url(url, href) for href in hrefs])

        for desturl in desturls:
            add_edge(url, desturl)

        return desturls
