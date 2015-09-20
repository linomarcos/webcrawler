from django.db import models

class Node(models.Model):
    url = models.TextField(max_length=1024)

class Edge(models.Model):
    tail = models.ForeignKey(Node, related_name='tail_node')
    head = models.ForeignKey(Node, related_name='head_node')


def get_node(url):
    """INSERT/SELECT statement for Node table"""
    try:
        node = Node.objects.get(url__exact=url)
    except Node.DoesNotExist:
        node = Node.objects.create(url=url)
        node.save()

    return node


def add_edge(src_url, dest_url):
    """Adds a record to Edge table defined by "head" and "tail" nodes"""
    tail = get_node(src_url)
    head = get_node(dest_url)

    if Edge.objects.filter(head__exact=head, tail__exact=tail).exists():
        return

    edge = Edge.objects.create(tail=tail, head=head)
    edge.save()

