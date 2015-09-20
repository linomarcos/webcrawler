import json
import yaml
import redis
import logging


class CrawlerNode(object):
    """Implements logic for distributed Breadth-First Search"""

    QUEUE_NS = 'crawler:queue'
    VISITED_NS = 'crawler:visited'

    def __init__(self, redis_config, graph_api):
        """
        @redis_config: Redis client connection data
        @graph_api:    interface to the data layer; see README for spec.
        """
        self._graph_api = graph_api

        self._redis = redis.StrictRedis(**redis_config)
        logging.info('using Redis connection %s', redis_config)

    def enqueue(self, url, depth=0):
        data = json.dumps(dict(url=url, depth=depth))
        self._redis.rpush(self.QUEUE_NS, data)

    def _dequeue(self):
        data = json.loads(self._redis.lpop(self.QUEUE_NS))
        return data['url'], data['depth']

    def _has_next(self):
        return self._redis.exists(self.QUEUE_NS)

    def _mark_visited(self, url):
        self._redis.sadd(self.VISITED_NS, url)

    def _is_visited(self, url):
        return self._redis.sismember(self.VISITED_NS, url)

    def reset(self):
        """Drops current BFS state"""
        logging.warn('dropping BFS state, queue depth = %d',
                     self._redis.llen(self.QUEUE_NS))
        self._redis.delete(self.QUEUE_NS, self.VISITED_NS)

    def start(self, max_depth):
        """Main entry point."""

        while self._has_next():
            url, depth = self._dequeue()
            if depth > max_depth or self._is_visited(url):
                continue
            self._mark_visited(url)
            for new_url in self._graph_api.adjacent_nodes(url):
                self.enqueue(new_url, depth + 1)
