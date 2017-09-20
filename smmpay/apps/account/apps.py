from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AccountConfig(AppConfig):
    name = 'smmpay.apps.account'
    label = 'account'
    verbose_name = _('Account')

    def ready(self):
        import smmpay.apps.account.signals