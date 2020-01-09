from django.utils.translation import ugettext_lazy as _

# Templates for different models
SEO_INFORMATION_TEMPLATES = {
    'advert': {
        'vk': {
            'meta_title': _('VKontakte advertising - %s'),
            'meta_description': _('Sell ​​or buy ads on VKontakte'),
            'meta_keywords': _('Buy VKontakte ads, VK exchange, find advertisers for VKontakte group, sell ads in VK'),
        },
        'youtube': {
            'meta_title': _('Youtube advertising - %s'),
            'meta_description': _('Sell ​​or buy Youtube ads'),
            'meta_keywords': _('Buy ads on YouTube, youtube channel exchange, find advertisers for YouTube channel, '
                               'sell ads on YouTube'),
        },
        'facebook': {
            'meta_title': _('Facebook advertising - %s'),
            'meta_description': _('Sell ​​or buy Facebook ads'),
            'meta_keywords': _('Buy advertising on facebook, the exchange of facebook groups, find advertisers for '
                               'facebook groups, sell advertising on facebook'),
        },
        'instagram': {
            'meta_title': _('Instagram advertising - %s'),
            'meta_description': _('Sell ​​or buy Instagram ads'),
            'meta_keywords': _('Buy ads on instagram, instagram account exchange, find advertisers for instagram, '
                               'sell ads on instagram'),
        },
        'twitter': {
            'meta_title': _('Twitter advertising - %s'),
            'meta_description': _('Sell ​​or buy Twitter ads'),
            'meta_keywords': _('Buy advertising on twitter, the exchange of twitter groups, find advertisers for '
                               'twitter groups, sell advertising on twitter'),
        },
        'telegram': {
            'meta_title': _('Telegram advertising - %s'),
            'meta_description': _('Sell ​​or buy Telegram ads'),
            'meta_keywords': _('Buy telegram advertising, telegram exchange of channels, find advertisers for telegram '
                               'channel, sell advertising in telegram'),
        },
        'tiktok': {
            'meta_title': _('Tiktok advertising - %s'),
            'meta_description': _('Sell ​​or buy adverts at Tiktok'),
            'meta_keywords': _('Buy adverts in Tik Tok, Tiktok exchange, find advertisers for Tiktok, sell '
                               'advertisements in Tiktok'),
        }
    }
}
