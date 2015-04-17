from django.db import models

class Node(models.Model):
    url = models.CharField(max_length=512)
    status = models.IntegerField(default=0)
    title = models.TextField(blank=True)

class Edge(models.Model):
    tail = models.ForeignKey(Node, related_name='tail_node')
    head = models.ForeignKey(Node, related_name='head_node')
    text = models.TextField(blank=True)


class API(object):
    """API layer for models. The main design principles are:

        1. All nodes are indexed by a URL, and accessor methods take the URL
           as an argument, not the node itself.

        2. There is not separate method to "add" a node: the getter, which
           takes a URL argument, adds an entry if it does not exist.

        3. All extra fields of a `Node` are set using keyword arguments of the
           `update_node` method.

           In particular, the `is_visited` method checks the `Node.status` field,
           so marking the node as visited is handled by updating its status to
           something nonzero (eg, a timestamp).
    """

    def get_node(self, url):
        """Returns the `Node` associated to the URL, creating one if necessary.
        """
        try:
            node = Node.objects.get(url__exact=url)
        except Node.DoesNotExist:
            node = Node.objects.create(url=url)
            node.save()
        return node

    def add_edge(self, src_url, dest_url, **kwargs):
        """Creates an edge, defined by "tail" and "head" nodes of an `Edge`.

        @param src_url, dest_url [str]: defines the tail and head, respectively.
        @keyword text [str]: supplies the `Edge.text` field
        """
        tail = self.get_node(src_url)
        head = self.get_node(dest_url)
        if Edge.objects.filter(head__exact=head, tail__exact=tail).exists():
            return

        text = kwargs.get('text', '')
        edge = Edge.objects.create(tail=tail, head=head, text=text)
        edge.save()

    def update_node(self, url, **kwargs):
        """Keyword arguments supply values to the other properties of `Node`.
        """
        node = self.get_node(url)
        for key in ['status', 'title']:
            if key in kwargs:
                setattr(node, key, kwargs[key])
        node.save()

    def is_visited(self, url):
        try:
            node = Node.objects.get(url__exact=url)
            return node.status != 0
        except Node.DoesNotExist:
            return False

