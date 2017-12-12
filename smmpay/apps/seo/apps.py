from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SeoConfig(AppConfig):
    name = 'smmpay.apps.seo'
    label = 'seo'
    verbose_name = _('SEO')

    def ready(self):
        import smmpay.apps.seo.signals
