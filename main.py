#!/usr/bin/env python

import yaml
import logging
import argparse
from crawler_node import CrawlerNode
from webgraph.webgraph_api import WebGraphAPI


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Webcrawler interface')
    parser.add_argument('--config', default='config.yaml', help='config file to use')
    parser.add_argument('--reset', action='store_true',
                        help='send reset command to crawler, DROPS ALL STATE')
    parser.add_argument('--seedfile', help='list of seed URLs, one per line.')
    parser.add_argument('--webgraph', type=int, default=None,
                        help='crawl webgraph to specified max-depth')
    args = parser.parse_args()

    config = yaml.load(open(args.config))
    logging.basicConfig(**config['logging_config'])

    client = CrawlerNode(args.config, None)

    if args.reset:
        client.reset()

    if args.seedfile:
        for url in open(args.seedfile):
            client.enqueue(url.strip())

    if args.webgraph:
        api = WebGraphAPI()
        client = CrawlerNode(args.config, api)
        client.start(args.webgraph)

