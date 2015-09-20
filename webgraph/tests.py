from django.test import TestCase
from models import Node, Edge

class GraphTest(TestCase):

    def test_get_node(self):
        """smoke test for models.get_node"""

        from models import get_node

        self.assertEqual(0, Node.objects.count())

        node = get_node('foo')
        self.assertEqual('foo', node.url)
        self.assertEqual(1, Node.objects.count())

    def test_add_edge(self):
        """smoke test for models add_edge"""
        from models import add_edge

        self.assertEqual(0, Edge.objects.count())

        add_edge('foo', 'bar')
        self.assertEqual(1, Edge.objects.count())

        add_edge('foo', 'bar')
        self.assertEqual(1, Edge.objects.count())

        add_edge('foo', 'baz')
        self.assertEqual(2, Edge.objects.count())
