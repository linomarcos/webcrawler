import re
import logging
import requests
from bs4 import BeautifulSoup
from urlparse import urlsplit, urlunsplit
from models import API as ModelAPI

requests_logger = logging.getLogger('requests')
requests_logger.setLevel(logging.WARN)

def load_page(url, timeout=2):
    """Returns the parsed HTML of a page or `None` if the page cannot be loaded.
    """
    try:
        head = requests.head(url, timeout=timeout)
        if head.status_code != 200:
            raise Exception('response status %d' % head.status_code)
        if head.headers.get('content-type').lower().find('html') == -1:
            raise Exception('not HTML content-type')

        logging.info('fetching %s', url)
        resp = requests.get(url, timeout=timeout)
        return BeautifulSoup(resp.text)

    except Exception as ex:
        logging.warning('%s: %s', url, ex)
        return None

def get_clean_url(href, base_url=None):
    """Returns an absolute URL/path from an `href`, assuming a valid HTTP URL
    can be created. If one cannot, `None` is returned.

    @param base_url [str|None]: a base url from which to build the absolute path
           if `href` is a relative path.
    """
    scheme, netloc, path, _, _ = urlsplit(href)

    if scheme and not re.match(r'^http', scheme):
        return None

    if scheme and netloc:
        return urlunsplit((scheme, netloc, path, None, None))

    if base_url and path:
        base_scheme, base_netloc, _, _, _ = urlsplit(base_url)
        return urlunsplit((base_scheme, base_netloc, path, None, None))

    return None


class WebGraphAPI(object):
    """Graph API interface for crawler_node.CrawlerNode.
    """
    _model_api = ModelAPI()

    def is_visited(self, url):
        return self._model_api.is_visited(url)

    def add_edge(self, url, outbound_link):
        self._model_api.add_edge(url, outbound_link['url'], text=outbound_link['text'])

    def adjacent_nodes(self, url):
        """Marks a node as "visited," and returns an _iterator_ of meta data for
        valid outbound links.
        """
        self._model_api.update_node(url, status=1)

        parsed_html = load_page(url)
        if not parsed_html:
            return

        title = parsed_html.title
        if title:
            self._model_api.update_node(url, title=title.get_text())

        for link in parsed_html.body.find_all('a'):
            if not link.get('href'):
                continue

            link_url = get_clean_url(link['href'], url)
            if not link_url:
                continue

            yield dict(url=link_url, text=link.get_text())

