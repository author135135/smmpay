import logging
import time

from datetime import timedelta

from django.db.models import Q
from django.core.management.base import BaseCommand
from django.utils import timezone

from smmpay.apps.advert.models import AdvertSocialAccount, SocialAccountConfirmationQueue

logger = logging.getLogger('db')


class Command(BaseCommand):
    help = 'Try to get confirmation for all adverts of social account type'

    def handle(self, *args, **options):
        logger.info('Social account confirmation start...')

        # Step 1: insert all new adverts to main queue
        social_accounts_in_queue = SocialAccountConfirmationQueue.objects.values('social_account')
        social_accounts = AdvertSocialAccount.objects.filter(confirmed=0).exclude(pk__in=social_accounts_in_queue)

        if social_accounts.exists():
            social_accounts_to_queue = []

            for social_account in social_accounts:
                queue_item = SocialAccountConfirmationQueue(social_account=social_account)
                social_accounts_to_queue.append(queue_item)

            SocialAccountConfirmationQueue.objects.bulk_create(social_accounts_to_queue)

        # Step 2: get adverts from main queue for handling, update theirs status and refresh from DB
        social_accounts_ids = SocialAccountConfirmationQueue.objects.filter(
            Q(status=SocialAccountConfirmationQueue.QUEUE_STATUS_NEW) |
            Q(status=SocialAccountConfirmationQueue.QUEUE_STATUS_ERROR,
              attempts__lt=SocialAccountConfirmationQueue.QUEUE_MAX_ATTEMPTS,
              last_start__lte=timezone.now() - timedelta(days=1)) |
            Q(status=SocialAccountConfirmationQueue.QUEUE_STATUS_ERROR,
              attempts__lt=SocialAccountConfirmationQueue.QUEUE_MAX_ATTEMPTS,
              last_start=None)).values('pk')[:20]

        social_accounts_ids = [advert_id['pk'] for advert_id in social_accounts_ids]

        SocialAccountConfirmationQueue.objects.filter(pk__in=social_accounts_ids).update(
            status=SocialAccountConfirmationQueue.QUEUE_STATUS_PROGRESS,
            last_start=timezone.now())

        queue_items = SocialAccountConfirmationQueue.objects.filter(pk__in=social_accounts_ids).select_related(
            'social_account')

        # Step 3: process each advert
        for queue_item in queue_items:
            queue_item.new_attempt()

            link = queue_item.social_account.link
            code = queue_item.social_account.confirmation_code

            try:
                parser = AdvertSocialAccount.get_parser(queue_item.social_account.social_network.code)
                confirmed = parser.get_account_confirmation(url=link, code=code)
            except Exception as e:
                logger.exception(e)

                confirmed = False

            if confirmed:
                queue_item.social_account.confirmed = True
                queue_item.social_account.save()

                queue_item.set_status(SocialAccountConfirmationQueue.QUEUE_STATUS_SUCCESS)
            else:
                queue_item.set_status(SocialAccountConfirmationQueue.QUEUE_STATUS_ERROR)

            time.sleep(5)

        # Step 4: clean main queue
        SocialAccountConfirmationQueue.objects.filter(
            Q(status=SocialAccountConfirmationQueue.QUEUE_STATUS_SUCCESS) |
            Q(status=SocialAccountConfirmationQueue.QUEUE_STATUS_ERROR,
              attempts__gte=SocialAccountConfirmationQueue.QUEUE_MAX_ATTEMPTS) |
            Q(social_account__confirmed=True)).delete()

        logger.info('Social account confirmation end.')
