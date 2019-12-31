import logging
import sys
import requests
import re

import vk
import facebook
import tweepy

from django.conf import settings

from vk.exceptions import VkAPIError
from apiclient.discovery import build
from apiclient.errors import HttpError
from bs4 import BeautifulSoup

from urllib import parse

logger = logging.getLogger('db')


class SocialNetworkConnector(object):
    """
    Abstract interface for social network connectors
    """
    def __init__(self, *args, **kwargs):
        self.account_link = parse.urlparse(kwargs.get('account_link', None))

    def get_account_info(self):
        raise NotImplementedError()


class VkSocialNetworkConnector(SocialNetworkConnector):
    """
    Connector for work with vk.com
    """
    def __init__(self, *args, **kwargs):
        super(VkSocialNetworkConnector, self).__init__(*args, **kwargs)

        # @TODO Keep eyes on it, seems vk changed their workflow
        session = vk.AuthSession(app_id=settings.SOCIAL_NETWORK_VK_APP_ID,
                                 user_login=settings.SOCIAL_NETWORK_VK_LOGIN,
                                 user_password=settings.SOCIAL_NETWORK_VK_PASSWORD)
        # session = vk.Session()
        self.api = vk.API(session)

    def get_account_info(self):
        result = {}

        path_parts = self.account_link.path.strip('/').split('/')

        object_keyword = path_parts[-1]

        if object_keyword is None:
            return result

        try:
            response = self.api.groups.getById(group_id=object_keyword,
                                               fields='name,members_count,photo_200', v=5.103)[0]

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
        super(FacebookSocialNetworkConnector, self).__init__(*args, **kwargs)

        self.api = facebook.GraphAPI(version='2.9')
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
        super(TwitterSocialNetworkConnector, self).__init__(*args, **kwargs)

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
        super(YoutubeSocialNetworkConnector, self).__init__(*args, **kwargs)

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


class InstagramSocialNetworkConnector(SocialNetworkConnector):
    def get_account_info(self):
        result = {}

        try:
            headers = {'x-requested-with': 'XMLHttpRequest'}
            response = requests.get('%s?__a=1' % self.account_link.geturl(), headers=headers)

            if response.status_code == 200:
                json_data = response.json()

                result['title'] = json_data['graphql']['user']['full_name']
                result['subscribers'] = json_data['graphql']['user']['edge_followed_by']['count']
                result['logo'] = json_data['graphql']['user']['profile_pic_url_hd']
        except Exception as e:
            logger.exception(e)

        return result


class TelegramSocialNetworkConnector(SocialNetworkConnector):
    """
    Connector for work with telegram.
    For now we just parse account page by BeautifulSoup.
    """
    def get_account_info(self):
        result = {}

        try:
            response = requests.get(self.account_link.geturl())

            if response.status_code == 200:
                parser = BeautifulSoup(response.content, features='lxml')

                element_logo = parser.select_one('.tgme_page_photo_image')

                if element_logo is not None:
                    result['logo'] = element_logo.attrs['src']

                element_title = parser.select_one('.tgme_page_title')

                if element_title is not None:
                    result['title'] = element_title.text.strip()

                element_subscribers = parser.select_one('.tgme_page_extra')

                if element_subscribers is not None:
                    re_match = re.match(r'[\d ]+', element_subscribers.text)

                    if re_match is not None:
                        subscribers = re_match.group()
                        subscribers = subscribers.replace(' ', '')

                        try:
                            result['subscribers'] = int(subscribers)
                        except ValueError:
                            pass
        except Exception as e:
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
