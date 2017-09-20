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

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField()
    image = models.ImageField(blank=True, upload_to='blog/posts/%Y/%m/%d')
    status = models.SmallIntegerField(choices=STATUSES, default=DRAFT, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published_objects = PublishedPostManager()

    class Meta:
        db_table = 'blog_post'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post', kwargs={'slug': self.slug})
