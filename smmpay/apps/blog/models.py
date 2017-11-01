from django.db import models
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class PublishedPostManager(models.Manager):
    def get_queryset(self):
        return super(PublishedPostManager, self).get_queryset().filter(status=Post.PUBLISHED)


class Post(models.Model):
    DRAFT = 0
    PUBLISHED = 1

    STATUSES = (
        (DRAFT, _('draft')),
        (PUBLISHED, _('published'))
    )

    title = models.CharField(_('title'), max_length=255)
    url = models.SlugField(_('URL'), max_length=255, unique=True)
    content = models.TextField(_('content'))
    image = models.ImageField(_('main image'), blank=True, upload_to='blog/posts/%Y/%m/%d')
    status = models.SmallIntegerField(_('status'), choices=STATUSES, default=DRAFT, db_index=True)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    updated = models.DateTimeField(_('updated'), auto_now=True)

    objects = models.Manager()
    published_objects = PublishedPostManager()

    class Meta:
        db_table = 'blog_post'
        ordering = ('-id',)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post', kwargs={'slug': self.url})
