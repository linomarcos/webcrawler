import os
import logging
from unittest import TestCase
import sqlite3
import crawler

ROOTPATH = os.path.dirname(crawler.__file__)
SCHEMAPATH = os.path.join(ROOTPATH, 'config/schema.sql')
TESTDB = os.path.join(ROOTPATH, 'testdb')

class TestDataLayer(TestCase):
    @classmethod
    def setUpClass(cls):
        logging.info('loading schema from %s', SCHEMAPATH)
        init_script = open(SCHEMAPATH).read()

        logging.info('creating %s', TESTDB)
        if os.path.isfile(TESTDB):
            os.unlink(TESTDB)
        conn = sqlite3.connect(TESTDB)
        cursor = conn.cursor()
        cursor.executescript(init_script)

    @classmethod
    def tearDownClass(cls):
        os.unlink(TESTDB)

    def test_id_idempotence(self):
        unit = crawler.Crawler(TESTDB)
        foo_expected = unit.get_node_id('foo')
        foo_actual = unit.get_node_id('foo')
        self.assertEqual(foo_expected, foo_actual)

    def test_edge_idempotence(self):
        unit = crawler.Crawler(TESTDB)
        foo_id = unit.get_node_id('foo')
        bar_id = unit.get_node_id('bar')
        unit.add_edge(foo_id, bar_id)
        unit.add_edge(foo_id, bar_id)

        cursor = unit.conn.cursor()
        cursor.execute("""
            select count(*) from edges
            where tail_id = ? and head_id = ?""",
            (foo_id, bar_id))
        (count,) = cursor.fetchone()
        self.assertEqual(1, count)

    def test_edge_validity(self):
        unit = crawler.Crawler(TESTDB)
        foo_id = unit.get_node_id('foo')

        cursor = unit.conn.cursor()
        cursor.execute('select max(id) from nodes')
        (maxid,) = cursor.fetchone()
        invalid_id = maxid + 1
        unit.add_edge(foo_id, invalid_id)

        cursor.execute("""
            select count(*) from edges
            where tail_id = ? and head_id = ?""",
            (foo_id, invalid_id))
        (count,) = cursor.fetchone()
        self.assertEqual(0, count)
