import logging
import sys
from urllib import parse

import vk
import facebook
import tweepy

from vk.exceptions import VkAPIError
from apiclient.discovery import build
from apiclient.errors import HttpError

from django.conf import settings

logger = logging.getLogger('db')

if settings.DEBUG:
    import os

    os.environ['https_proxy'] = 'https://104.236.27.71:3128'


class SocialNetworkConnector(object):
    """
    Abstract interface for social network connectors
    """
    def get_account_info(self):
        raise NotImplementedError()


class VkSocialNetworkConnector(SocialNetworkConnector):
    """
    Connector for work with vk.com
    """
    def __init__(self, *args, **kwargs):
        self.account_link = parse.urlparse(kwargs.get('account_link', None))
        # @TODO Check why vk.AuthSession not works
        """session = vk.AuthSession(app_id=settings.SOCIAL_NETWORK_VK_APP_ID,
                                 user_login=settings.SOCIAL_NETWORK_VK_LOGIN,
                                 user_password=settings.SOCIAL_NETWORK_VK_PASSWORD)"""
        session = vk.Session()
        self.api = vk.API(session)

    def get_account_info(self):
        result = {}

        path_parts = self.account_link.path.strip('/').split('/')

        object_keyword = path_parts[-1]

        if object_keyword is None:
            return result

        try:
            response = self.api.groups.getById(group_id=object_keyword, fields='name,members_count,photo_200')[0]

            result['title'] = response['name']
            result['subscribers'] = response['members_count']
            result['logo'] = response['photo_200']
        except VkAPIError as e:
            logger.exception(e)

        return result


class FacebookSocialNetworkConnector(SocialNetworkConnector):
    """
    Connector for work with facebook
    """
    def __init__(self, *args, **kwargs):
        self.account_link = parse.urlparse(kwargs.get('account_link', '').strip())

        self.api = facebook.GraphAPI(version='2.7')
        self.api.access_token = self.api.get_app_access_token(settings.SOCIAL_NETWORK_FACEBOOK_KEY,
                                                              settings.SOCIAL_NETWORK_FACEBOOK_SECRET)

    def get_account_info(self):
        result = {}

        path_parts = self.account_link.path.strip('/').split('/')

        object_keyword = path_parts[-1]

        if object_keyword is None:
            return result

        try:
            response = self.api.get_object(object_keyword, fields='name')

            result['title'] = response['name']
        except facebook.GraphAPIError as e:
            logger.exception(e)

        return result


class TwitterSocialNetworkConnector(SocialNetworkConnector):
    """
    Connector for work with twitter
    """
    def __init__(self, *args, **kwargs):
        self.account_link = parse.urlparse(kwargs.get('account_link', None))

        auth = tweepy.OAuthHandler(settings.SOCIAL_NETWORK_TWITTER_API_KEY, settings.SOCIAL_NETWORK_TWITTER_API_SECRET)
        auth.set_access_token(settings.SOCIAL_NETWORK_TWITTER_ACCESS_TOKEN,
                              settings.SOCIAL_NETWORK_TWITTER_ACCESS_TOKEN_SECRET)

        self.api = tweepy.API(auth)

    def get_account_info(self):
        result = {}

        path_parts = self.account_link.path.strip('/').split('/')

        object_keyword = path_parts[-1]

        if not object_keyword:
            return result

        try:
            user = self.api.get_user(object_keyword)

            result['title'] = user.name
            result['subscribers'] = user.followers_count
            result['logo'] = user.profile_image_url.replace('_normal', '')
        except Exception as e:
            logger.exception(e)

        return result


class YoutubeSocialNetworkConnector(SocialNetworkConnector):
    """
    Connector for work with youtube
    """
    def __init__(self, *args, **kwargs):
        self.account_link = parse.urlparse(kwargs.get('account_link', None))

        self.api = build('youtube', 'v3', developerKey=settings.SOCIAL_NETWORK_YOUTUBE_API_KEY)

    def get_account_info(self):
        result = {}

        path_parts = self.account_link.path.strip('/').split('/')

        object_keyword = path_parts[-1]

        if not object_keyword:
            return result

        try:
            response = self.api.channels().list(id=object_keyword, part='snippet,statistics').execute()

            if response['pageInfo']['totalResults']:
                result['title'] = response['items'][0]['snippet']['title']
                result['subscribers'] = response['items'][0]['statistics']['subscriberCount']
                result['logo'] = response['items'][0]['snippet']['thumbnails']['high']['url']
        except HttpError as e:
            logger.exception(e)

        return result


def get_api_connector(social_network, *args, **kwargs):
    if social_network is None:
        raise Exception('Can not identify social network')

    klass = '{}SocialNetworkConnector'.format(social_network.title())

    if hasattr(sys.modules[__name__], klass):
        return getattr(sys.modules[__name__], klass)(*args, **kwargs)
    else:
        raise Exception('API connector for social network `{}` does not exists'.format(social_network))
