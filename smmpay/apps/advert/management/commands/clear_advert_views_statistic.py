import logging

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from smmpay.apps.advert.models import AdvertViewsStatistic

logger = logging.getLogger('db')


class Command(BaseCommand):
    help = 'Clear old adverts views statistic'

    def handle(self, *args, **options):
        logger.info('Clear adverts view statistic start...')

        AdvertViewsStatistic.objects.filter(date__lte=timezone.now() - timedelta(days=1)).delete()

        logger.info('Clear adverts view statistic end.')
