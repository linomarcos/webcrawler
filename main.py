#!/usr/bin/env python

import os
import sys
import json
import yaml
import logging
import argparse
import beanstalkc
from crawler_node import CrawlerNode
from webgraph.webgraph_api import WebGraphAPI

ROOT_PATH = os.path.dirname(__file__)
DEFAULT_CONFIG = os.path.join(ROOT_PATH, 'config.yaml')

def seed_queue(config, seedfile):
    client = beanstalkc.Connection(**config['beanstalk_config'])
    print 'connected at %s' % config['beanstalk_config']

    print 'reading from seed file %s' % seedfile
    for url in map(str.strip, open(args.seedfile)):
        jobdefn = dict(url=url, depth=0)
        client.put(json.dumps(jobdefn))


parser = argparse.ArgumentParser(description='Webcrawler interface')
parser.add_argument('--config', type=str, default=DEFAULT_CONFIG)
parser.add_argument('--seedfile', type=str, help='list of seed URLs, one per line.')
parser.add_argument('--crawl', action='store_true')

if __name__ == '__main__':
    args = parser.parse_args()

    config = yaml.load(open(args.config))
    logging.basicConfig(**config['logging_config'])

    if args.seedfile:
        seed_queue(config, args.seedfile)

    if args.crawl:
        api = WebGraphAPI()
        worker = CrawlerNode(api, args.config)
        worker.start()

