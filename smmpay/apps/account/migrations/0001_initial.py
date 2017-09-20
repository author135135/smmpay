# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import smmpay.apps.advert.helpers
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('email', models.EmailField(unique=True, max_length=254)),
                ('is_admin', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_profile_public', models.BooleanField(default=True)),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now)),
                ('groups', models.ManyToManyField(blank=True, to='auth.Group', verbose_name='groups', related_query_name='user', related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.')),
                ('user_permissions', models.ManyToManyField(blank=True, to='auth.Permission', verbose_name='user permissions', related_query_name='user', related_name='user_set', help_text='Specific permissions for this user.')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'db_table': 'account_user',
            },
        ),
        migrations.CreateModel(
            name='EmailChangeToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('token', models.CharField(max_length=64)),
                ('expiry_date', models.DateTimeField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'account_email_token',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to=smmpay.apps.advert.helpers.RenameFile('account/profiles'))),
                ('first_name', models.CharField(verbose_name='first name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', blank=True, max_length=30)),
                ('phone_number', models.CharField(verbose_name='phone number', blank=True, max_length=16, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{9,15}$', message='Phone number must be entered in the format: +999999999')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='profile')),
            ],
            options={
                'verbose_name': 'user profile',
                'verbose_name_plural': 'user profiles',
                'db_table': 'account_user_profile',
            },
        ),
        migrations.AlterUniqueTogether(
            name='emailchangetoken',
            unique_together=set([('user', 'email')]),
        ),
    ]
