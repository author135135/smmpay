from django.db.models import signals
from django.dispatch import receiver

from .models import Advert
from .tasks import send_notification_for_author


@receiver(signals.post_init, sender=Advert)
def save_old_model_status(instance, **kwargs):
    instance._old_status = instance.status


@receiver(signals.post_save, sender=Advert)
def create_notification_for_author_task(created, instance, **kwargs):
    if (created is False and instance.status != instance._old_status and
       instance.status in (Advert.ADVERT_STATUS_PUBLISHED,
                           Advert.ADVERT_STATUS_VIOLATION)):
        send_notification_for_author.delay(instance.id)
