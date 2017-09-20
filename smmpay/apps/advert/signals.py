import os

from django.db.models import signals
from django.dispatch import receiver
from .models import Advert


@receiver(signals.pre_save, sender=Advert)
def delete_advert_social_account_logo_file(sender, instance, created=False, **kwargs):
    if created is False:
        advert = Advert.objects.select_related('social_account').get(pk=instance.pk)

        if (advert.social_account.logo and advert.social_account.logo != instance.social_account.logo and
            os.path.exists(advert.social_account.logo)):
            os.remove(advert.social_account.logo)


@receiver(signals.pre_delete, sender=Advert)
def delete_advert_social_account_logo_file(sender, instance, **kwargs):
    if instance.social_account.logo and os.path.exists(instance.social_account.logo):
        os.remove(instance.social_account.logo)
