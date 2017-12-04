from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AdvertConfig(AppConfig):
    name = 'smmpay.apps.advert'
    label = 'advert'
    verbose_name = _('Advert')

    def ready(self):
        import smmpay.apps.advert.signals
