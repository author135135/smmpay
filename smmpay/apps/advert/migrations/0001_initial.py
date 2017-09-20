# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import smmpay.apps.advert.helpers


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Advert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('advert_type', models.TextField(default='social_account', choices=[('social_account', 'Social account')], max_length=25)),
                ('price', models.IntegerField()),
                ('views', models.IntegerField(default=0)),
                ('enabled_by_author', models.BooleanField(default=True)),
                ('enabled_by_admin', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(related_name='adverts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'advert',
                'verbose_name_plural': 'adverts',
                'db_table': 'advert_advert',
                'ordering': ('-pk',),
            },
        ),
        migrations.CreateModel(
            name='AdvertSocialAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to=smmpay.apps.advert.helpers.RenameFile('advert/social_accounts/%Y/%m/%d'))),
                ('link', models.URLField()),
                ('subscribers', models.IntegerField()),
                ('confirmed', models.BooleanField(default=False)),
                ('confirmation_code', models.TextField()),
                ('advert', models.OneToOneField(to='advert.Advert', related_name='social_account')),
            ],
            options={
                'db_table': 'advert_advert_social_account',
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'category',
                'verbose_name_plural': 'categories',
                'db_table': 'advert_category',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='Discussion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('advert', models.ForeignKey(related_name='discussions', to='advert.Advert')),
            ],
            options={
                'verbose_name': 'discussion',
                'verbose_name_plural': 'discussions',
                'db_table': 'advert_discussion',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='DiscussionMessage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('message', models.TextField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('discussion', models.ForeignKey(related_name='discussion_messages', to='advert.Discussion')),
            ],
            options={
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
                'db_table': 'advert_discussion_message',
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='DiscussionMessageView',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('viewed', models.BooleanField(default=True)),
                ('view_date', models.DateTimeField(auto_now_add=True)),
                ('message', models.ForeignKey(related_name='views', to='advert.DiscussionMessage')),
            ],
            options={
                'verbose_name': 'view',
                'verbose_name_plural': 'views',
                'db_table': 'advert_discussion_message_view',
            },
        ),
        migrations.CreateModel(
            name='DiscussionUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('discussion', models.ForeignKey(related_name='discussion_users', to='advert.Discussion')),
                ('user', models.ForeignKey(related_name='discussion_users', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'discussion user',
                'verbose_name_plural': 'discussion users',
                'db_table': 'advert_discussion_user',
            },
        ),
        migrations.CreateModel(
            name='FavoriteAdvert',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('advert', models.ForeignKey(related_name='favorite_adverts', to='advert.Advert')),
                ('user', models.ForeignKey(related_name='favorite_adverts', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'favorite',
                'verbose_name_plural': 'favorites',
                'db_table': 'advert_favorite_advert',
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('position', models.CharField(choices=[('top_menu', 'Top menu'), ('bottom_menu', 'Bottom menu')], max_length=32)),
            ],
            options={
                'verbose_name': 'menu',
                'verbose_name_plural': 'menu',
                'db_table': 'advert_menu',
            },
        ),
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=64)),
                ('url', models.CharField(max_length=255)),
                ('menu', models.ForeignKey(related_name='menu_items', to='advert.Menu')),
            ],
            options={
                'verbose_name': 'menu item',
                'verbose_name_plural': 'menu items',
                'db_table': 'advert_menu_item',
            },
        ),
        migrations.CreateModel(
            name='Phrase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('lang', models.CharField(max_length=2)),
                ('phrase', models.TextField()),
            ],
            options={
                'db_table': 'advert_phrase',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name': 'region',
                'verbose_name_plural': 'regions',
                'db_table': 'advert_region',
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='SocialAccountConfirmationQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('status', models.CharField(default='new', choices=[('new', 'New'), ('success', 'Success'), ('progress', 'In progress'), ('error', 'Error')], max_length=10)),
                ('attempts', models.SmallIntegerField(default=0)),
                ('last_start', models.DateTimeField(blank=True, null=True)),
                ('social_account', models.ForeignKey(to='advert.AdvertSocialAccount')),
            ],
            options={
                'db_table': 'advert_advert_social_account_confirmation',
            },
        ),
        migrations.CreateModel(
            name='SocialNetwork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
                ('code', models.CharField(max_length=25)),
                ('url', models.URLField()),
            ],
            options={
                'verbose_name': 'social network',
                'verbose_name_plural': 'social networks',
                'db_table': 'advert_social_network',
            },
        ),
        migrations.AlterUniqueTogether(
            name='socialnetwork',
            unique_together=set([('code', 'url')]),
        ),
        migrations.AddField(
            model_name='discussionmessageview',
            name='user',
            field=models.ForeignKey(to='advert.DiscussionUser'),
        ),
        migrations.AddField(
            model_name='discussionmessage',
            name='sender',
            field=models.ForeignKey(to='advert.DiscussionUser'),
        ),
        migrations.AddField(
            model_name='discussion',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='advert.DiscussionUser'),
        ),
        migrations.AddField(
            model_name='advertsocialaccount',
            name='category',
            field=models.ForeignKey(on_delete=None, to='advert.Category'),
        ),
        migrations.AddField(
            model_name='advertsocialaccount',
            name='region',
            field=models.ForeignKey(on_delete=None, to='advert.Region'),
        ),
        migrations.AddField(
            model_name='advertsocialaccount',
            name='social_network',
            field=models.ForeignKey(on_delete=None, to='advert.SocialNetwork'),
        ),
        migrations.AlterUniqueTogether(
            name='favoriteadvert',
            unique_together=set([('advert', 'user')]),
        ),
    ]
