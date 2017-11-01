from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BlogConfig(AppConfig):
    name = 'smmpay.apps.blog'
    label = 'blog'
    verbose_name = _('Blog')
