from urllib.parse import urlparse
from django.db import models
from django.db.models import FieldDoesNotExist
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import query as advert_query
from .utils import api_connectors, parsers
from .helpers import RenameFile

import random


User = settings.AUTH_USER_MODEL


class ExtraQuerysetManager(models.Manager):
    """
    Provide method for extends QuerySet by raw SQL
    """
    def get_extra_queryset(self, *args, **kwargs):
        qs = self.get_queryset()

        select_items = kwargs.pop('select_items', None)
        select = {}

        if select_items is not None:
            for item in select_items:
                keyword = '%s__%s' % (self.model._meta.model_name, item)
                keyword = keyword.upper()

                extra_query = getattr(advert_query, keyword, None)

                if extra_query is not None:
                    select[item] = extra_query

        return qs.extra(select=select, **kwargs)


class DiscussionManager(ExtraQuerysetManager):
    def get_queryset(self):
        return super(DiscussionManager, self).get_queryset().select_related('advert', 'advert__social_account')


class MessageManager(ExtraQuerysetManager):
    def get_queryset(self):
        return super(MessageManager, self).get_queryset().select_related('sender__user__profile')


class AdvertManager(ExtraQuerysetManager):
    def get_queryset(self):
        qs = super(AdvertManager, self).get_queryset()
        qs = qs.select_related('social_account', 'social_account__category', 'social_account__region',
                               'social_account__social_network', 'author__profile')

        return qs


class EnabledAdvertManager(AdvertManager):
    def get_queryset(self):
        return super(EnabledAdvertManager, self).get_queryset().filter(enabled_by_author=True, enabled_by_admin=True)


class FavoriteAdvertManager(models.Manager):
    def get_queryset(self):
        return super(FavoriteAdvertManager, self).get_queryset().select_related('advert', 'user',
                                                                                'advert__social_account',
                                                                                'advert__social_account__category',
                                                                                'advert__social_account__region')


class Menu(models.Model):
    title = models.CharField(max_length=64)
    position = models.CharField(max_length=32, choices=settings.ADVERT_MENU_POSITIONS)

    class Meta:
        db_table = 'advert_menu'
        verbose_name = _('menu')
        verbose_name_plural = _('menu')

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(max_length=64)
    url = models.CharField(max_length=255)
    menu = models.ForeignKey(Menu, related_name='menu_items')

    class Meta:
        db_table = 'advert_menu_item'
        verbose_name = _('menu item')
        verbose_name_plural = _('menu items')

    def __str__(self):
        return self.title


class Region(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        db_table = 'advert_region'
        ordering = ('title',)
        verbose_name = _('region')
        verbose_name_plural = _('regions')

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(max_length=255)

    class Meta:
        db_table = 'advert_category'
        ordering = ('title',)
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.title


class SocialNetwork(models.Model):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=25)
    url = models.URLField()

    class Meta:
        db_table = 'advert_social_network'
        ordering = ('pk',)
        verbose_name = _('social network')
        verbose_name_plural = _('social networks')
        unique_together = ('code', 'url')

    def __str__(self):
        return self.title


class Phrase(models.Model):
    lang = models.CharField(max_length=2)
    phrase = models.TextField()

    class Meta:
        db_table = 'advert_phrase'

    def __str__(self):
        return self.phrase

    def get_info(self):
        return '[{}]: {}...'.format(self.lang.upper(), self.phrase[:50])

    @classmethod
    def get_rand_phrase(cls, lang=None):
        if lang is not None:
            records_count = cls.objects.filter(lang=lang).count()
        else:
            records_count = cls.objects.count()

        if records_count > 0:
            index = random.randint(0, records_count - 1)

            if lang is not None:
                return cls.objects.filter(lang=lang)[index]
            else:
                return cls.objects.all()[index]
        return None


class Advert(models.Model):
    ADVERT_TYPE_SOCIAL_ACCOUNT = 'social_account'

    ADVERT_TYPES = (
        (ADVERT_TYPE_SOCIAL_ACCOUNT, _('Social account')),
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    advert_type = models.TextField(max_length=25, choices=ADVERT_TYPES, default=ADVERT_TYPE_SOCIAL_ACCOUNT)
    author = models.ForeignKey(User, related_name='adverts', on_delete=models.CASCADE)
    price = models.IntegerField()
    views = models.IntegerField(default=0)
    enabled_by_author = models.BooleanField(default=True)
    enabled_by_admin = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = AdvertManager()
    enabled_objects = EnabledAdvertManager()

    class Meta:
        db_table = 'advert_advert'
        ordering = ('-pk',)
        verbose_name = _('advert')
        verbose_name_plural = _('adverts')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('advert:advert', kwargs={'pk': self.pk})

    @classmethod
    def get_default_advert_type(cls):
        try:
            return cls._meta.get_field('advert_type').get_default()
        except FieldDoesNotExist:
            return None

    def add_view(self, request):
        ip = request.META['REMOTE_ADDR']

        views_statistic_obj, created = self.views_statistic.get_or_create(ip=ip)

        if created:
            self.views += 1
            self.save()

        return created


class AdvertSocialAccount(models.Model):
    SOCIAL_NETWORKS_URLS = {
        'vk': ['www.vk.com', 'vk.com', 'm.vk.com'],
        'facebook': ['www.facebook.com', 'facebook.com'],
        'instagram': ['www.instagram.com', 'instagram.com'],
        'twitter': ['www.twitter.com', 'twitter.com', 'm.twitter.com', 'mobile.twitter.com'],
        'youtube': ['www.youtube.com', 'youtube.com']
    }

    advert = models.OneToOneField(Advert, related_name='social_account', on_delete=models.CASCADE)
    logo = models.ImageField(upload_to=RenameFile('offer/social_accounts/%Y/%m/%d'), blank=True, null=True)
    link = models.URLField()
    subscribers = models.IntegerField()
    social_network = models.ForeignKey(SocialNetwork, on_delete=None)
    category = models.ForeignKey(Category, on_delete=None)
    region = models.ForeignKey(Region, on_delete=None)
    confirmed = models.BooleanField(default=False)
    confirmation_code = models.TextField()

    class Meta:
        db_table = 'advert_advert_social_account'

    def __str__(self):
        return self.advert.title

    @classmethod
    def get_api_connector(cls, social_network=None, **kwargs):
        """
        Return instance of API connector class or raise Exception if worker doesn't exists
        """
        if social_network is None:
            social_network = cls.get_social_network(kwargs.get('account_link', None))

        return api_connectors.get_api_connector(social_network, **kwargs)

    @classmethod
    def get_parser(cls, social_network=None, **kwargs):
        """
        Return instance of parser class or raise Exception if worker doesn't exists
        """
        if social_network is None:
            social_network = cls.get_social_network(kwargs.get('account_link', None))

        return parsers.get_parser(social_network, **kwargs)

    @classmethod
    def get_social_network(cls, link):
        """
        Identify network by link
        """
        url_info = urlparse(link)

        for network, urls in cls.SOCIAL_NETWORKS_URLS.items():
            if url_info.netloc in urls:
                return network
        return None


class AdvertViewsStatistic(models.Model):
    advert = models.ForeignKey(Advert, related_name='views_statistic', on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'advert_advert_views_statistic'


class SocialAccountConfirmationQueue(models.Model):
    QUEUE_STATUS_NEW = 'new'
    QUEUE_STATUS_SUCCESS = 'success'
    QUEUE_STATUS_PROGRESS = 'progress'
    QUEUE_STATUS_ERROR = 'error'

    QUEUE_MAX_ATTEMPTS = 5

    QUEUE_STATUSES = (
        (QUEUE_STATUS_NEW, _('New')),
        (QUEUE_STATUS_SUCCESS, _('Success')),
        (QUEUE_STATUS_PROGRESS, _('In progress')),
        (QUEUE_STATUS_ERROR, _('Error'))
    )

    social_account = models.ForeignKey(AdvertSocialAccount, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=QUEUE_STATUSES, default='new')
    attempts = models.SmallIntegerField(default=0)
    last_start = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'advert_advert_social_account_confirmation'

    def __str__(self):
        return _('Social account({}) {}').format(self.social_account.pk, self.get_status_display())

    def set_status(self, status):
        self.status = status

        self.save()

    def new_attempt(self):
        self.attempts += 1
        self.last_start = timezone.now()

        self.save()


class FavoriteAdvert(models.Model):
    advert = models.ForeignKey(Advert, related_name='favorite_adverts', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='favorite_adverts', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    objects = FavoriteAdvertManager()

    class Meta:
        db_table = 'advert_favorite_advert'
        ordering = ('-id',)
        verbose_name = _('favorite')
        verbose_name_plural = _('favorites')
        unique_together = ('advert', 'user')


class Discussion(models.Model):
    advert = models.ForeignKey(Advert, related_name='discussions', on_delete=models.CASCADE)
    users = models.ManyToManyField(User, through='DiscussionUser')
    created = models.DateTimeField(auto_now_add=True)

    objects = DiscussionManager()

    class Meta:
        db_table = 'advert_discussion'
        verbose_name = _('discussion')
        verbose_name_plural = _('discussions')
        ordering = ('pk',)

    def __str__(self):
        return self.advert.title

    @classmethod
    def create_discussion(cls, advert, users=None):
        discussion = cls.objects.create(advert=advert)

        if isinstance(users, (list, tuple)):
            discussion.add_users(users)

        return discussion

    def add_user(self, user):
        return self.discussion_users.create(user=user)

    def add_users(self, users):
        discussion_users = []

        user_model = get_user_model()

        for user in users:
            discussion_user = user

            if isinstance(user, user_model):
                discussion_user = DiscussionUser(discussion=self, user=user)

            discussion_users.append(discussion_user)

        return self.discussion_users.bulk_create(discussion_users)

    def add_message(self, user, message):
        sender = user

        user_model = get_user_model()

        if isinstance(user, user_model):
            sender = self.discussion_users.get(user=user)

        return self.discussion_messages.create(sender=sender, message=message)


class DiscussionUser(models.Model):
    discussion = models.ForeignKey(Discussion, related_name='discussion_users', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='discussion_users', on_delete=models.CASCADE)

    class Meta:
        db_table = 'advert_discussion_user'
        verbose_name = _('discussion user')
        verbose_name_plural = _('discussion users')

    def __str__(self):
        return str(self.user)


class DiscussionMessage(models.Model):
    discussion = models.ForeignKey(Discussion, related_name='discussion_messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(DiscussionUser, on_delete=models.CASCADE)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    objects = MessageManager()

    class Meta:
        db_table = 'advert_discussion_message'
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        ordering = ('pk',)

    def __str__(self):
        return self.message

    def mark_as_viewed(self, user):
        try:
            message_view = self.views.get(user=user)
        except DiscussionMessageView.DoesNotExist:
            message_view = self.views.create(message=self, user=user, viewed=True)

        if message_view.viewed is False:
            message_view.viewed = True
            message_view.save()

        return True


class DiscussionMessageView(models.Model):
    message = models.ForeignKey(DiscussionMessage, related_name='views', on_delete=models.CASCADE)
    user = models.ForeignKey(DiscussionUser, on_delete=models.CASCADE)
    viewed = models.BooleanField(default=True)
    view_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'advert_discussion_message_view'
        verbose_name = _('view')
        verbose_name_plural = _('views')

    def __str__(self):
        return self.message
