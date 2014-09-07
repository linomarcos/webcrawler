from django.test import TestCase
from models import Node, Edge, API

class APITest(TestCase):

    def test_get_node(self):
        """Smoke test for API.get_node
        """
        api = API()
        self.assertEqual(0, Node.objects.count())

        node = api.get_node('foo')
        self.assertEqual('foo', node.url)
        self.assertEqual(0, node.status)
        self.assertEqual('', node.title)

        _ = api.get_node('foo')
        self.assertEqual(1, Node.objects.count())

    def test_add_edge(self):
        """Smoke test for API.add_edge
        """
        api = API()
        self.assertEqual(0, Edge.objects.count())

        api.add_edge('foo', 'bar')
        self.assertEqual(1, Edge.objects.count())

        api.add_edge('foo', 'bar')
        self.assertEqual(1, Edge.objects.count())

        api.add_edge('foo', 'baz')
        self.assertEqual(2, Edge.objects.count())

    def test_search_methods(self):
        """Smoke tests for API.is_visited, API.update_node.
        """
        api = API()
        self.assertFalse(api.is_visited('foo'))

        api.update_node('foo', bar='blech')  # node does not exist
        self.assertFalse(api.is_visited('foo'))

        _ = api.get_node('foo')
        self.assertFalse(api.is_visited('foo'))

        api.update_node('foo', status=1)
        self.assertTrue(api.is_visited('foo'))
