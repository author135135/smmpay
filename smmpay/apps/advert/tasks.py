from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.sites.models import Site

from celery import shared_task

from .models import Advert


@shared_task(bind=True, autoretry_for=(Exception,), default_retry_delay=10,
             max_retries=3, time_limit=10)
def send_notification_for_author(self, advert_id):
    advert = Advert.objects.get(pk=advert_id)

    email_subject_template_name = ''
    email_body_template_name = ''

    if advert.status == Advert.ADVERT_STATUS_PUBLISHED:
        email_subject_template_name = 'advert/emails/advert_status_published_email_subject.txt'
        email_body_template_name = 'advert/emails/advert_status_published_email.html'
    elif advert.status == Advert.ADVERT_STATUS_VIOLATION:
        email_subject_template_name = 'advert/emails/advert_status_violation_email_subject.txt'
        email_body_template_name = 'advert/emails/advert_status_violation_email.html'

    user = advert.author

    current_site = Site.objects.get_current()

    email_context = {
        'domain': current_site.domain,
        'advert': advert,
        'user': user
    }

    subject = render_to_string(email_subject_template_name, email_context)
    subject = ''.join(subject.splitlines())

    message = render_to_string(email_body_template_name, email_context)

    email_message = EmailMultiAlternatives(subject, from_email=settings.DEFAULT_FROM_EMAIL, to=[user.email])
    email_message.attach_alternative(message, 'text/html')

    email_message.send()
