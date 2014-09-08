import os
import json
import yaml
import logging
import beanstalkc


ROOT_PATH = os.path.dirname(__file__)
DEFAULT_CONFIG = os.path.join(ROOT_PATH, 'config.yaml')

class CrawlerNode(object):
    """Implements logic for distributed Breadth-First Search.
    """
    CLIENT_TIMEOUT = 2

    def __init__(self, graph_api, config_file=DEFAULT_CONFIG):
        """
        @param graph_api: interface to the data layer; see README for spec.
        @param config_file: path/to/yaml-file with application wide settings.
        """
        self._graph_api = graph_api

        config = yaml.load(open(config_file))
        logging.info('CrawlerNode: loaded %s', config_file)

        beanstalk_config = config['beanstalk_config']
        self._q_client = beanstalkc.Connection(**beanstalk_config)
        logging.info('CrawlerNode connected: %s', beanstalk_config)

        self._max_depth = config['max_depth']

    def _get_new_job(self, last_job=None):
        """Acknowledges the last_job as done and fetches a new job.
        """
        if last_job:
            last_job.delete()
        return self._q_client.reserve(timeout=self.CLIENT_TIMEOUT)

    def start(self):
        job = self._get_new_job()
        while job:
            params = json.loads(job.body)
            if (params['depth'] > self._max_depth or
                self._graph_api.is_visited(params['url'])):

                job = self._get_new_job(job)
                continue

            for link in self._graph_api.adjacent_nodes(params['url']):
                self._graph_api.add_edge(params['url'], link)
                new_params = {
                    'url': link['url'],
                    'depth': params['depth'] + 1,
                }
                self._q_client.put(json.dumps(new_params))

            job = self._get_new_job(job)
