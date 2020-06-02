from currencies.models import Currency

from .models import SocialNetwork


def additional_context(request):
    # Fix for template tags `currency`
    try:
        default_currency = Currency.active.default()
    except Currency.DoesNotExist:
        default_currency = None

    return {
        'default_social_network': SocialNetwork.objects.first(),
        'CURRENCY_DEFAULT': default_currency
    }
