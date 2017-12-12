from django.utils.translation import ugettext_lazy as _

# Templates for different models
SEO_INFORMATION_TEMPLATES = {
    'advert': {
        'vk': {
            'meta_title': _('Sell group, public vkontakte - %s'),
            'meta_description': _('Sell ​​or buy a group, public vkontakte. Safe transaction.'),
            'meta_keywords': _('Buy group vkontakte, buy group vk, buy public, buy a community, buy a group in vk'),
        },
        'youtube': {
            'meta_title': _('Sell a Youtube channel - %s'),
            'meta_description': _('Sell ​​or buy a Youtube channel. Safe transaction.'),
            'meta_keywords': _('Buy YouTube channel, buy youtube channel, buy YouTube, buy youtube, buy channel'),
        },
        'facebook': {
            'meta_title': _('Sell a Facebook group - %s'),
            'meta_description': _('Sell ​​or buy a Facebook group. Safe transaction.'),
            'meta_keywords': _('Buy group Facebook, buy group fb, buy public, buy community, buy group in facebook'),
        },
        'instagram': {
            'meta_title': _('Sell an Instagram account - %s'),
            'meta_description': _('Sell ​​or buy an Instagram account. Safe transaction.'),
            'meta_keywords': _('Buy account instagram, buy account inst, buy account, buy account in instagram'),
        },
        'twitter': {
            'meta_title': _('Sell a Twitter account - %s'),
            'meta_description': _('Sell ​​or buy a Twitter account. Safe transaction.'),
            'meta_keywords': _('Buy account twitter, buy account tw, buy account, buy account in twitter'),
        },
        'telegram': {
            'meta_title': _('Selling the Telegram channel - %s'),
            'meta_description': _('Sell ​​or buy the Telegram channel. Safe transaction.'),
            'meta_keywords': _('Buy a telegram channel, buy telegram, buy a channel'),
        },
    }
}
