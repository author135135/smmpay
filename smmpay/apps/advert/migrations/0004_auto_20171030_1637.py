# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-10-30 14:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import smmpay.apps.advert.helpers


class Migration(migrations.Migration):

    dependencies = [
        ('advert', '0003_auto_20171011_1419'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='socialnetwork',
            options={'ordering': ('order', 'pk'), 'verbose_name': 'social network', 'verbose_name_plural': 'social networks'},
        ),
        migrations.RenameField(
            model_name='phrase',
            old_name='lang',
            new_name='language',
        ),
        migrations.RemoveField(
            model_name='advertsocialaccount',
            name='category',
        ),
        migrations.AddField(
            model_name='advert',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='adverts', to='advert.Category'),
        ),
        migrations.AddField(
            model_name='socialnetwork',
            name='order',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='socialnetwork',
            name='urls',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='advert',
            name='advert_type',
            field=models.CharField(choices=[('social_account', 'Social account')], default='social_account', max_length=25),
        ),
        migrations.AlterField(
            model_name='advertsocialaccount',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=smmpay.apps.advert.helpers.RenameFile('offer/social_accounts/%Y/%m/%d')),
        ),
        migrations.AlterField(
            model_name='advertsocialaccount',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='social_accounts', to='advert.Region'),
        ),
        migrations.AlterField(
            model_name='advertsocialaccount',
            name='social_network',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='social_accounts', to='advert.SocialNetwork'),
        ),
        migrations.AlterField(
            model_name='socialnetwork',
            name='code',
            field=models.CharField(max_length=25, unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='socialnetwork',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='socialnetwork',
            name='url',
        ),
    ]