from .models import SocialNetwork


def additional_context(request):
    return {
        'default_social_network': SocialNetwork.objects.first()
    }
