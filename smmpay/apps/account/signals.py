from django.db.models import signals
from django.dispatch import receiver
from .models import User, Profile


@receiver(signals.post_save, sender=User)
def create_or_save_user_profile(sender, instance, **kwargs):
    if not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()
