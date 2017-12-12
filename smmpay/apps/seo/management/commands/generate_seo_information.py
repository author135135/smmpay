import logging

from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.utils import translation
from django.conf import settings

from smmpay.apps.seo.models import PageSeoInformation
from smmpay.apps.seo.templates import SEO_INFORMATION_TEMPLATES

logger = logging.getLogger('db')


class Command(BaseCommand):
    help = """Generate seo information for models passed in --models argument.
              Note: --models should be in format `app_label.model_name`"""

    def add_arguments(self, parser):
        parser.add_argument('--models', nargs='+', type=str)

    def handle(self, *args, **options):
        logger.info('Generate seo information start...')

        translation.activate(settings.LANGUAGE_CODE)

        models = options.get('models')

        if not models:
            raise CommandError("Missing required argument --models")

        for model in models:
            try:
                app_label, model_name = model.split('.')
            except ValueError:
                print(self.style.NOTICE(
                    'Model `%s` passed in incorrect format, '
                    'please use the following format `app_label.model_name`.' % model))

                continue

            try:
                model_cls = apps.get_model(app_label=app_label, model_name=model_name)
            except LookupError as e:
                logger.exception(e)

                continue

            templates = SEO_INFORMATION_TEMPLATES.get(model_name.lower(), None)

            if templates is None:
                logger.warning('No available templates for model `%s`' % model)

                continue

            bulk_objects = []

            for obj in model_cls.objects.iterator():
                if hasattr(obj, 'get_absolute_url'):
                    obj_url = getattr(obj, 'get_absolute_url')()
                else:
                    logger.warning('Model `%s` has no attribute `get_absolute_url`. Model was passed.' % model)

                    break

                if not PageSeoInformation.check_for_url(obj_url):
                    seo_information = {
                        'page_url': obj_url,
                        'meta_title': '',
                        'meta_description': '',
                        'meta_keywords': '',
                    }

                    # Use additional condition because templates can have different logic for making data
                    if model_name.lower() == 'advert':
                        social_network = obj.social_account.social_network.code
                        social_network_templates = templates.get(social_network, None)

                        if social_network_templates is not None:
                            seo_information['meta_title'] = social_network_templates['meta_title'] % obj.title
                            seo_information['meta_description'] = social_network_templates['meta_description']
                            seo_information['meta_keywords'] = social_network_templates['meta_keywords']

                    bulk_objects.append(PageSeoInformation(**seo_information))

            if len(bulk_objects) > 0:
                PageSeoInformation.objects.bulk_create(bulk_objects)

        translation.deactivate()

        logger.info('Generate seo information end.')
