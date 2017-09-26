# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('advert', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdvertViewsStatistic',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('advert', models.ForeignKey(related_name='views_statistic', to='advert.Advert')),
            ],
            options={
                'db_table': 'advert_advert_views_statistic',
            },
        ),
    ]
