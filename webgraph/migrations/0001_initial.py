# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Edge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.TextField(max_length=1024)),
            ],
        ),
        migrations.AddField(
            model_name='edge',
            name='head',
            field=models.ForeignKey(related_name='head_node', to='webgraph.Node'),
        ),
        migrations.AddField(
            model_name='edge',
            name='tail',
            field=models.ForeignKey(related_name='tail_node', to='webgraph.Node'),
        ),
    ]
