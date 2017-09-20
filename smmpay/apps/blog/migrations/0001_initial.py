# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(unique=True, max_length=255)),
                ('content', models.TextField()),
                ('image', models.ImageField(blank=True, upload_to='blog/posts/%Y/%m/%d')),
                ('status', models.SmallIntegerField(default=0, choices=[(0, 'draft'), (1, 'published')], db_index=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'blog_post',
            },
        ),
    ]
