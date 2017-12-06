import sys
import time
import os

from selenium import webdriver
from bs4 import BeautifulSoup

from django.conf import settings


class WebClient(object):
    def __init__(self):
        self.browser = None

        driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'webdrivers', 'chromedriver')

        if not os.path.exists(driver_path):
            raise Exception('Driver does not exists')

        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")

        self.browser = webdriver.Chrome(driver_path, chrome_options=chrome_options)

    def get_page(self, url):
        self.browser.get(url)

    def get_page_content(self, url=None, login_required=False, **kwargs):
        if url is not None:
            self.get_page(url)

            if login_required:
                self.login_on_page(**kwargs)

        return self.browser.page_source

    def login_on_page(self, login_id, password_id, login, password, submit_id):
        element_login = self.browser.find_element_by_id(login_id)
        element_password = self.browser.find_element_by_id(password_id)

        element_login.send_keys(login)
        element_password.send_keys(password)

        element_submit = self.browser.find_element_by_id(submit_id)
        element_submit.submit()

        time.sleep(5)

    def __del__(self):
        if isinstance(self.browser, webdriver.Chrome):
            self.browser.quit()


class SocialNetworkParser(object):
    """
    Abstract interface for social network parsers
    """

    def get_account_confirmation(self, url, code):
        """
        Method should implement logic for getting confirmation from social network
        """
        raise NotImplementedError


class VkSocialNetworkParser(SocialNetworkParser):
    ACCOUNT_CONFIRMATION_SELECTOR = 'span.current_text'

    def get_account_confirmation(self, url, code):
        client = WebClient()

        parser = BeautifulSoup(client.get_page_content(url), 'lxml')
        element = parser.select_one(self.ACCOUNT_CONFIRMATION_SELECTOR)

        if element is not None:
            return element.text.strip() == code.strip()

        return False


class FacebookSocialNetworkParser(object):
    ACCOUNT_CONFIRMATION_SELECTOR = '#groupsDescriptionBox .text_exposed_root'

    def get_account_confirmation(self, url, code):
        client = WebClient()

        page_content = client.get_page_content(url, True, login_id='email', password_id='pass',
                                               login=settings.SOCIAL_NETWORK_FACEBOOK_LOGIN,
                                               password=settings.SOCIAL_NETWORK_FACEBOOK_PASSWORD,
                                               submit_id='loginbutton')

        parser = BeautifulSoup(page_content, 'lxml')
        element = parser.select_one(self.ACCOUNT_CONFIRMATION_SELECTOR)

        if element is not None:
            text = element.find(text=True, recursive=False)
            text += element.select_one('.text_exposed_show').text

            return text.strip() == code.strip()

        return False


class TwitterSocialNetworkParser(object):
    ACCOUNT_CONFIRMATION_SELECTOR = 'p.ProfileHeaderCard-bio'

    def get_account_confirmation(self, url, code):
        client = WebClient()

        parser = BeautifulSoup(client.get_page_content(url), 'lxml')
        element = parser.select_one(self.ACCOUNT_CONFIRMATION_SELECTOR)

        if element is not None:
            return element.text.strip() == code.strip()

        return False


class YoutubeSocialNetworkParser(object):
    ACCOUNT_CONFIRMATION_SELECTOR = '#description'

    def get_account_confirmation(self, url, code):
        client = WebClient()

        parser = BeautifulSoup(client.get_page_content('{}/about'.format(url.rstrip('/'))), 'lxml')
        element = parser.select_one(self.ACCOUNT_CONFIRMATION_SELECTOR)

        if element is not None:
            return element.text.strip() == code.strip()

        return False


class InstagramSocialNetworkParser(object):
    ACCOUNT_CONFIRMATION_SELECTOR = 'header ul + div span'

    def get_account_confirmation(self, url, code):
        client = WebClient()

        parser = BeautifulSoup(client.get_page_content(url), 'lxml')
        element = parser.select_one(self.ACCOUNT_CONFIRMATION_SELECTOR)

        if element is not None:
            return element.text.strip() == code.strip()

        return False


class TelegramSocialNetworkParser(object):
    ACCOUNT_CONFIRMATION_SELECTOR = '.tgme_page_description'

    def get_account_confirmation(self, url, code):
        client = WebClient()

        parser = BeautifulSoup(client.get_page_content(url), 'lxml')
        element = parser.select_one(self.ACCOUNT_CONFIRMATION_SELECTOR)

        if element is not None:
            return element.text.strip() == code.strip()

        return False


def get_parser(social_network, *args, **kwargs):
    if social_network is None:
        raise Exception('Can not identify social network')

    klass = '{}SocialNetworkParser'.format(social_network.title())

    if hasattr(sys.modules[__name__], klass):
        return getattr(sys.modules[__name__], klass)(*args, **kwargs)
    else:
        raise Exception('Parser for social network `{}` does not exists'.format(social_network))
