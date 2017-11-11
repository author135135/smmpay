# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-11 16:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='title')),
                ('url', models.SlugField(max_length=255, unique=True, verbose_name='URL')),
                ('content', models.TextField(verbose_name='content')),
                ('image', models.ImageField(blank=True, upload_to='blog/posts/%Y/%m/%d', verbose_name='main image')),
                ('status', models.SmallIntegerField(choices=[(0, 'draft'), (1, 'published')], db_index=True, default=0, verbose_name='status')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated', models.DateTimeField(auto_now=True, verbose_name='updated')),
            ],
            options={
                'verbose_name_plural': 'posts',
                'ordering': ('-pk',),
                'db_table': 'blog_post',
                'verbose_name': 'post',
            },
        ),
    ]
