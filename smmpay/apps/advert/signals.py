from django.db.models import signals
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.sites.models import Site

from .models import Advert


@receiver(signals.post_init, sender=Advert)
def save_old_model_status(instance, **kwargs):
    instance._old_status = instance.status


@receiver(signals.post_save, sender=Advert)
def send_notification_for_author(created, instance, raw, update_fields, using, **kwargs):
    email_subject_template_name = ''
    email_body_template_name = ''

    need_send_email = True

    if created is False and instance.status != instance._old_status:
        if instance.status == Advert.ADVERT_STATUS_PUBLISHED:
            email_subject_template_name = 'advert/emails/advert_status_published_email_subject.txt'
            email_body_template_name = 'advert/emails/advert_status_published_email.html'
        elif instance.status == Advert.ADVERT_STATUS_VIOLATION:
            email_subject_template_name = 'advert/emails/advert_status_violation_email_subject.txt'
            email_body_template_name = 'advert/emails/advert_status_violation_email.html'
        else:
            need_send_email = False

        if need_send_email:
            user = instance.author

            current_site = Site.objects.get_current()

            email_context = {
                'domain': current_site.domain,
                'advert': instance,
                'user': user
            }

            subject = render_to_string(email_subject_template_name, email_context)
            subject = ''.join(subject.splitlines())

            message = render_to_string(email_body_template_name, email_context)

            email_message = EmailMultiAlternatives(subject, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
            email_message.attach_alternative(message, 'text/html')

            email_message.send()
