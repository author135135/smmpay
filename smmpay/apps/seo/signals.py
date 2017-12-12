from django.db.models import signals
from django.dispatch import receiver
from django.core.urlresolvers import reverse
from django.contrib.flatpages.models import FlatPage

from smmpay.apps.advert.models import Advert, SocialNetwork

from .models import PageSeoInformation
from .templates import SEO_INFORMATION_TEMPLATES


@receiver(signals.post_save, sender=Advert)
def generate_seo_information_for_advert(instance, created, **kwargs):
    """
    Generate SEO information for new objects.
    """
    templates = SEO_INFORMATION_TEMPLATES.get('advert', None)

    advert_url = reverse('advert:advert', kwargs={'pk': instance.pk})

    if created and not PageSeoInformation.check_for_url(advert_url) and templates is not None:
        social_network = instance.social_account.social_network.code
        social_network_templates = templates.get(social_network, None)

        if social_network_templates is not None:
            seo_information = {
                'page_url': advert_url,
                'meta_title': social_network_templates['meta_title'] % instance.title,
                'meta_description': social_network_templates['meta_description'],
                'meta_keywords': social_network_templates['meta_keywords'],
            }

            PageSeoInformation.objects.create(**seo_information)


@receiver(signals.post_delete, sender=Advert)
@receiver(signals.post_delete, sender=FlatPage)
@receiver(signals.post_delete, sender=SocialNetwork)
def get(using, instance, **kwargs):
    """
    Delete seo information objects for instances that have `get_absolute_url` method
    """
    if hasattr(instance, 'get_absolute_url'):
        obj_url = getattr(instance, 'get_absolute_url')()

        PageSeoInformation.objects.filter(page_url=obj_url).delete()
