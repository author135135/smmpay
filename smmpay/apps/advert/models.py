import random

from urllib.parse import urlparse
from datetime import timedelta

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
        qs = qs.select_related('social_account', 'category', 'social_account__region',
                               'social_account__social_network', 'author__profile')

        return qs


class PublishedAdvertManager(AdvertManager):
    def get_queryset(self):
        qs = super(PublishedAdvertManager, self).get_queryset().filter(enabled_by_author=True,
                                                                       status=Advert.ADVERT_STATUS_PUBLISHED)

        return qs


class FavoriteAdvertManager(models.Manager):
    def get_queryset(self):
        return super(FavoriteAdvertManager, self).get_queryset().select_related('advert', 'advert__category', 'user',
                                                                                'advert__social_account',
                                                                                'advert__social_account__region')


class Menu(models.Model):
    title = models.CharField(_('title'), max_length=64)
    position = models.CharField(_('menu position'), max_length=32, choices=settings.ADVERT_MENU_POSITIONS)

    class Meta:
        db_table = 'advert_menu'
        verbose_name = _('menu')
        verbose_name_plural = _('menu')

    def __str__(self):
        return self.title


class MenuItem(models.Model):
    title = models.CharField(_('title'), max_length=64)
    url = models.CharField(_('URL'), max_length=255)
    menu = models.ForeignKey(verbose_name=_('menu'), to=Menu, related_name='menu_items')

    class Meta:
        db_table = 'advert_menu_item'
        verbose_name = _('menu item')
        verbose_name_plural = _('menu items')

    def __str__(self):
        return self.title


class Region(models.Model):
    title = models.CharField(_('title'), max_length=255)

    class Meta:
        db_table = 'advert_region'
        ordering = ('title',)
        verbose_name = _('region')
        verbose_name_plural = _('regions')

    def __str__(self):
        return self.title


class Category(models.Model):
    title = models.CharField(_('title'), max_length=255)

    class Meta:
        db_table = 'advert_category'
        ordering = ('title',)
        verbose_name = _('category')
        verbose_name_plural = _('categories')

    def __str__(self):
        return self.title


class SocialNetwork(models.Model):
    title = models.CharField(_('title'), max_length=255)
    code = models.CharField(_('network code'), max_length=25, unique=True)
    urls = models.TextField(_('URLs'))
    order = models.SmallIntegerField(_('order'), default=0)

    class Meta:
        db_table = 'advert_social_network'
        ordering = ('order', 'pk')
        verbose_name = _('social network')
        verbose_name_plural = _('social networks')

    def __str__(self):
        return self.title

    @classmethod
    def get_social_network(cls, link):
        """
        Identify network by link
        """
        url_info = urlparse(link)

        try:
            social_network = cls.objects.get(urls__icontains=url_info.netloc)
        except cls.DoesNotExist:
            social_network = None

        return social_network


class Phrase(models.Model):
    language = models.CharField(_('language'), max_length=2)
    phrase = models.TextField(_('phrase'))

    class Meta:
        db_table = 'advert_phrase'
        ordering = ('pk',)
        verbose_name = _('phrase')
        verbose_name_plural = _('phrases')

    def __str__(self):
        return self.phrase

    def get_info(self):
        return '[{}]: {}...'.format(self.language.upper(), self.phrase[:50])

    @classmethod
    def get_rand_phrase(cls, language=None):
        if language is not None:
            records_count = cls.objects.filter(language=language).count()
        else:
            records_count = cls.objects.count()

        if records_count > 0:
            index = random.randint(0, records_count - 1)

            if language is not None:
                return cls.objects.filter(language=language)[index]
            else:
                return cls.objects.all()[index]
        return None


class Advert(models.Model):
    ADVERT_TYPE_SOCIAL_ACCOUNT = 'social_account'

    ADVERT_TYPES = (
        (ADVERT_TYPE_SOCIAL_ACCOUNT, _('Social account')),
    )

    ADVERT_STATUS_PUBLISHED = 'published'
    ADVERT_STATUS_MODERATION = 'moderation'
    ADVERT_STATUS_VIOLATION = 'violation'

    ADVERT_STATUSES = (
        (ADVERT_STATUS_PUBLISHED, _('Published')),
        (ADVERT_STATUS_MODERATION, _('Moderation')),
        (ADVERT_STATUS_VIOLATION, _('Violation')),
    )

    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True)
    advert_type = models.CharField(_('type of advert'), max_length=25, choices=ADVERT_TYPES,
                                   default=ADVERT_TYPE_SOCIAL_ACCOUNT)
    category = models.ForeignKey(verbose_name=_('category'), to=Category, null=True, related_name='adverts',
                                 on_delete=models.SET_NULL)
    author = models.ForeignKey(verbose_name=_('author'), to=User, related_name='adverts', on_delete=models.CASCADE)
    price = models.PositiveIntegerField(_('price'))
    views = models.PositiveIntegerField(_('count of views'), default=0, editable=False)
    enabled_by_author = models.BooleanField(_('enabled by author'), default=True)
    status = models.CharField(_('status'), max_length=25, choices=ADVERT_STATUSES, default=ADVERT_STATUS_MODERATION)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    objects = AdvertManager()
    published_objects = PublishedAdvertManager()

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
        ip = request.META.get('HTTP_X_REAL_IP', request.META['REMOTE_ADDR'])

        if not self.views_statistic.filter(ip=ip, date__gte=timezone.now() - timedelta(days=1)).exists():
            self.views_statistic.create(ip=ip)

            self.views += 1
            self.save()

            return True

        return False

    def is_published(self):
        return self.status == self.ADVERT_STATUS_PUBLISHED


class AdvertSocialAccount(models.Model):
    advert = models.OneToOneField(verbose_name=_('advert'), to=Advert, related_name='social_account',
                                  on_delete=models.CASCADE)
    logo = models.ImageField(_('logo'), upload_to=RenameFile('offer/social_accounts/%Y/%m/%d'))
    link = models.URLField(_('account link'))
    subscribers = models.PositiveIntegerField(_('subscribers'))
    social_network = models.ForeignKey(verbose_name=_('social network'), to=SocialNetwork, null=True,
                                       related_name='social_accounts', on_delete=models.SET_NULL)
    region = models.ForeignKey(verbose_name=_('region'), to=Region, null=True, related_name='social_accounts',
                               on_delete=models.SET_NULL)
    confirmed = models.BooleanField(_('confirmed by author'), default=False)
    confirmation_code = models.TextField(_('confirmation code'))

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
            social_network_obj = SocialNetwork.get_social_network(kwargs.get('account_link', None))

            if social_network_obj is not None:
                social_network = social_network_obj.code

        return api_connectors.get_api_connector(social_network, **kwargs)

    @classmethod
    def get_parser(cls, social_network=None, **kwargs):
        """
        Return instance of parser class or raise Exception if worker doesn't exists
        """
        if social_network is None:
            social_network_obj = SocialNetwork.get_social_network(kwargs.get('account_link', None))

            if social_network_obj is not None:
                social_network = social_network_obj.code

        return parsers.get_parser(social_network, **kwargs)


class AdvertViewsStatistic(models.Model):
    advert = models.ForeignKey(to=Advert, related_name='views_statistic', on_delete=models.CASCADE)
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

    social_account = models.ForeignKey(verbose_name=_('social account'), to=AdvertSocialAccount,
                                       on_delete=models.CASCADE)
    status = models.CharField(_('status'), max_length=10, choices=QUEUE_STATUSES, default='new')
    attempts = models.SmallIntegerField(_('attempts count'), default=0)
    last_start = models.DateTimeField(_('last start'), blank=True, null=True)

    class Meta:
        db_table = 'advert_advert_social_account_confirmation'

    def __str__(self):
        return _('Social account({}) {}').format(self.social_account.pk, self.get_status_display())

    def set_status(self, status):
        self.status = status

        self.save()

    def new_attempt(self):
        self.attempts += 1

        self.save()


class FavoriteAdvert(models.Model):
    advert = models.ForeignKey(to=Advert, related_name='favorite_adverts', on_delete=models.CASCADE)
    user = models.ForeignKey(to=User, related_name='favorite_adverts', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    objects = FavoriteAdvertManager()

    class Meta:
        db_table = 'advert_favorite_advert'
        ordering = ('-pk',)
        verbose_name = _('favorite')
        verbose_name_plural = _('favorites')
        unique_together = ('advert', 'user')


class Discussion(models.Model):
    advert = models.ForeignKey(verbose_name=_('advert'), to=Advert, related_name='discussions',
                               on_delete=models.CASCADE)
    users = models.ManyToManyField(verbose_name=_('users'), to=User, through='DiscussionUser')
    created = models.DateTimeField(_('created'), auto_now_add=True)

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
    discussion = models.ForeignKey(verbose_name=_('discussion'), to=Discussion, related_name='discussion_users',
                                   on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name=_('user'), to=User, related_name='discussion_users', on_delete=models.CASCADE)

    class Meta:
        db_table = 'advert_discussion_user'
        verbose_name = _('discussion user')
        verbose_name_plural = _('discussion users')

    def __str__(self):
        return str(self.user)


class DiscussionMessage(models.Model):
    discussion = models.ForeignKey(verbose_name=_('discussion'), to=Discussion, related_name='discussion_messages',
                                   on_delete=models.CASCADE)
    sender = models.ForeignKey(verbose_name=_('message sender'), to=DiscussionUser, on_delete=models.CASCADE)
    message = models.TextField(_('message'))
    created = models.DateTimeField(_('created'), auto_now_add=True)

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
    message = models.ForeignKey(to=DiscussionMessage, related_name='views', on_delete=models.CASCADE)
    user = models.ForeignKey(to=DiscussionUser, on_delete=models.CASCADE)
    viewed = models.BooleanField(default=True)
    view_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'advert_discussion_message_view'
        verbose_name = _('view')
        verbose_name_plural = _('views')

    def __str__(self):
        return self.message.message
