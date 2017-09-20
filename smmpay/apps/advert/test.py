import vk
import facebook
import tweepy
import requests
import os
from bs4 import BeautifulSoup

from urllib import parse
from apiclient.discovery import build
from apiclient.errors import HttpError

SOCIAL_AUTH_FACEBOOK_KEY = '646704275472612'
SOCIAL_AUTH_FACEBOOK_SECRET = '883b6d06061578fef586a860b3fee95b'

SOCIAL_NETWORK_VK_LOGIN = 'leon135@ukr.net'
SOCIAL_NETWORK_VK_PASSWORD = 'Triolan135'
SOCIAL_NETWORK_VK_APP_ID = '6132654'

SOCIAL_NETWORK_OK_APP_ID = '1253182976'
SOCIAL_NETWORK_OK_APP_PUB_KEY = 'CBAPADLLEBABABABA'
SOCIAL_NETWORK_OK_APP_SEC_KEY = 'A5BED5C3D37DEAFE104CAD74'

SOCIAL_NETWORK_TWITTER_API_KEY = 'tNXNE6pFGsdhbxayfEntznINw'
SOCIAL_NETWORK_TWITTER_API_SECRET = 'o49PMixFo70PsAKZCkwiMUqtxHP51UzFvBNoWq3onEmci20CLj'
SOCIAL_NETWORK_TWITTER_ACCESS_TOKEN = '3928199133-5DAO51XoefWs8hw3KJHFdIQ6Y0TJvYgFpcd6bZT'
SOCIAL_NETWORK_TWITTER_ACCESS_TOKEN_SECRET = 'YLcc6j5WUL4rWOh7HyT14qEXAidoDm1JpdtOD6cAyAddp'

SOCIAL_NETWORK_YOUTUBE_API_KEY = 'AIzaSyD22IiosiG1KVShyD-m3googgOFk9Vsa8Q'

# os.environ['https_proxy'] = 'https://104.236.27.71:3128'


class SocialNetworkConnector(object):
    """
    Abstract interface for social network connectors
    """
    def get_account_info(self):
        raise NotImplementedError()


class FacebookSocialNetworkConnector(SocialNetworkConnector):
    def __init__(self, *args, **kwargs):
        self.account_link = parse.urlparse(kwargs.get('account_link', None))
        self.api = facebook.GraphAPI(version='2.7')
        self.api.access_token = self.api.get_app_access_token(SOCIAL_AUTH_FACEBOOK_KEY, SOCIAL_AUTH_FACEBOOK_SECRET)

    def get_account_info(self):
        result = {}
        object_keyword = None

        path = self.account_link.path.strip('/').split('/')
        # query_params = parse.parse_qs(self.account_link.query)

        if len(path) < 2:
            return result

        object_keyword = path[-1]

        # print(self.api.access_token)

        # return False

        try:
            # response = self.api.get_object(object_keyword, fields='name,fan_count,likes')
            response = self.api.request('search', {'q': 'yoptablja', 'type': 'page'})

            print(response)
        except facebook.GraphAPIError as e:
            print(e)
            response = {}

        result['title'] = response.get('name')
        result['likes'] = response.get('likes')

        return response

        # print(self.account_link.query)
        # print(self.api.get_object('BillGates'))


class VkSocialNetworkConnector(SocialNetworkConnector):
    def __init__(self, *args, **kwargs):
        self.account_link = parse.urlparse(kwargs.get('account_link', None))
        """session = vk.AuthSession(app_id=SOCIAL_NETWORK_VK_APP_ID,
                                 user_login=SOCIAL_NETWORK_VK_LOGIN,
                                 user_password=SOCIAL_NETWORK_VK_PASSWORD)"""

        session = vk.Session()
        self.api = vk.API(session)

        # app_id=None, user_login='', user_password='',

    def get_account_info(self):
        result = {}

        object_keyword = self.account_link.path.strip('/')

        if object_keyword is None:
            return result

        response = self.api.groups.getById(group_id=object_keyword, fields='name,members_count')[0]

        print(response)
        # print(self.api.users.get(user_ids=1))


class TwitterSocialNetworkConnector(SocialNetworkConnector):
    def __init__(self, *args, **kwargs):
        self.account_link = parse.urlparse(kwargs.get('account_link', None))

        auth = tweepy.OAuthHandler(SOCIAL_NETWORK_TWITTER_API_KEY, SOCIAL_NETWORK_TWITTER_API_SECRET)
        auth.set_access_token(SOCIAL_NETWORK_TWITTER_ACCESS_TOKEN, SOCIAL_NETWORK_TWITTER_ACCESS_TOKEN_SECRET)

        self.api = tweepy.API(auth)

        """self.api = twitter.Api(consumer_key=SOCIAL_NETWORK_TWITTER_API_KEY,
                               consumer_secret=SOCIAL_NETWORK_TWITTER_API_SECRET,
                               access_token_key=SOCIAL_NETWORK_TWITTER_ACCESS_TOKEN,
                               access_token_secret=SOCIAL_NETWORK_TWITTER_ACCESS_TOKEN_SECRET)"""

    def get_account_info(self):
        result = {
            'title': None,
            'likes': None
        }

        object_keyword = self.account_link.path.strip('/').split('/')[-1]

        try:
            user = self.api.get_user(object_keyword)

            result['title'] = user.name
            result['likes'] = user.followers_count
        except Exception as e:
            print(e)

        return result


class YoutubeSocialNetworkConnector(SocialNetworkConnector):
    def __init__(self, *args, **kwargs):
        self.account_link = parse.urlparse(kwargs.get('account_link', None))

        self.api = build('youtube', 'v3', developerKey=SOCIAL_NETWORK_YOUTUBE_API_KEY)

    def get_account_info(self):
        result = {}

        path = self.account_link.path.strip('/').split('/')

        object_keyword = path[-1]

        if not object_keyword:
            return result

        try:
            response = self.api.channels().list(id=object_keyword + '1121', part='snippet,statistics').execute()

            if response['pageInfo']['totalResults']:
                result['title'] = response['items'][0]['snippet']['title']
                result['likes'] = response['items'][0]['statistics']['subscriberCount']
        except HttpError as e:
            print(e)

        return result


# api = FacebookSocialNetworkConnector(account_link='https://www.facebook.com/tilllindemann/')
# api = YoutubeSocialNetworkConnector(account_link='https://www.youtube.com/user/dimakulinarkin')

# api = OKSocialNetworkConnector(account_link='https://www.ok.ru/group/48633148604651')

#api = VkSocialNetworkConnector(account_link='https://vk.com/club68944935')

#print(api.get_account_info())

# https://ok.ru/dk?cmd=GroupJoinDropdownBlock&st.jn.act=JOIN&st.jn.id=52891321893006&st.jn.blid=6522688920&st.cmd=altGroupMain&st.groupId=52891321893006&st.fFeed=on&st.referenceName=humspot&st._aid=AltGroupTopCardButtonsJoin

# res = html.parse('https://www.instagram.com/kimkardashian/')

# print(dir(res))

import sys
import time
from selenium import webdriver


class WebClient(object):
    def __init__(self):
        driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'utils', 'webdrivers/chromedriver')

        if not os.path.exists(driver_path):
            raise Exception('Driver does not exists')

        self.browser = webdriver.Chrome(driver_path)

    def __getattr__(self, item):
        return getattr(self.browser, item)

    def get_page_content(self, link):
        self.browser.get(link)

        return self.browser.page_source

    def __del__(self):
        pass
        # self.browser.quit()


class VkSocialNetworkParser(object):
    HTML_CONFIRMATION_QUERY = 'span.current_text'

    def get_account_confirmation(self, link, code):
        response = WebClient(link)

        parser = BeautifulSoup(response.html, 'lxml')

        print(dir(parser.select_one('span.current_text')))


class FacebookSocialNetworkParser(object):
    def get_account_confirmation(self, link, code):
        client = WebClient()

        open('/tmp/test.html', 'w').write(str(requests.get(link).content))

        print(client.get_page_content(link))

        # parser = BeautifulSoup(response.html, 'lxml')

        # print(parser.find_all('div', {'class': 'groupsEditDescriptionArea'}))


class TwitterSocialNetworkParser(object):
    def get_account_confirmation(self, link, code):
        response = requests.get(link)

        parser = BeautifulSoup(response.content, 'lxml')

        print(parser.select_one('p.ProfileHeaderCard-bio'))


class YoutubeSocialNetworkParser(object):
    def get_account_confirmation(self, link, code):
        response = requests.get('{}/about'.format(link.rstrip('/')))

        print(response.request.url)

        parser = BeautifulSoup(response.content, 'lxml')

        print(parser.select_one('div.about-description').text)


class InstagramSocialNetworkParser(object):
    def get_account_confirmation(self, link, code):
        client = WebClient()

        parser = BeautifulSoup(client.get_page_content(link), 'lxml')
        element = parser.select_one('div._bugdy span')

        # client.quit()

        if element is not None:
            print(element.text)
        else:
            print('Element is None')
        print()

"""link = 'https://www.facebook.com/groups/143494796235976/'
code = 'Вернуть деньги инвесторам и вознаградить тяжёлый труд своих сотрудников. Собственного бизнеса живыми, а только закрепит за равно.'

links = [link, link]

parser = FacebookSocialNetworkParser()
parser.get_account_confirmation(link, code)"""

link = 'https://www.facebook.com/groups/143494796235976/'

"""client = WebClient()

client.browser.get(link)

username = client.find_element_by_id("email")
password = client.find_element_by_id("pass")

username.send_keys("author135135@gmail.com")
password.send_keys("Triolan135")

submit_button = client.find_element_by_id("loginbutton")

submit_button.submit()

time.sleep(3)

print(open('/tmp/test.html', 'w').write(client.browser.page_source))"""

parser = BeautifulSoup(features='lxml')

"""element = parser.select_one('#groupsDescriptionBox .text_exposed_root')

t1 = element.find(text=True, recursive=False)
t2 = element.select_one('.text_exposed_show').text

print(t1 + t2)"""

# client.browser.quit()

print(dir(parser))
