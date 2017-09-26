import datetime
import time

from django.db import models, IntegrityError
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.crypto import salted_hmac, get_random_string
from django.utils.translation import ugettext_lazy as _

from smmpay.apps.advert.helpers import RenameFile


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, *args, **kwargs):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(email=UserManager.normalize_email(email))

        if not password:
            password = self.make_random_password()

        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_admin = True
        user.is_superuser = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_profile_public = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        db_table = 'account_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __unicode__(self):
        return self.email

    @property
    def is_staff(self):
        return self.is_admin

    def get_short_name(self):
        if self.profile.first_name:
            return self.profile.first_name
        return self.email

    def get_full_name(self):
        if self.profile.first_name and self.profile.last_name:
            return '{} {}'.format(self.profile.first_name, self.profile.last_name)
        return self.email

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(to=User, related_name='profile', on_delete=models.CASCADE)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=30, blank=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message=_('Phone number must be entered in the format: +999999999'))
    phone_number = models.CharField(_('phone number'), max_length=16, validators=[phone_regex], blank=True)

    class Meta:
        db_table = 'account_user_profile'
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return self.user.get_full_name()


class EmailChangeToken(models.Model):
    """
    Account application token generator model for change user email
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(max_length=254)
    token = models.CharField(max_length=64)
    expiry_date = models.DateTimeField(blank=False)

    class Meta:
        db_table = 'account_email_token'
        unique_together = ('user', 'email')

    @classmethod
    def make_token(cls, user, email):
        """
        Make a token and store it in DB
        """
        value = '%s%s%s' % (user.email, time.mktime(datetime.datetime.now().timetuple()), get_random_string(24))

        token = salted_hmac('EmailChangeToken', '%s%s' % (user.email, value)).hexdigest()[::2]
        expiry_date = timezone.now() + datetime.timedelta(days=settings.ACCOUNT_EMAIL_CHANGE_TIMEOUT_DAYS)

        try:
            obj = cls(user=user, email=email, token=token, expiry_date=expiry_date)
            obj.save()
        except IntegrityError:
            obj = cls.objects.get(user=user, email=email)
            obj.token = token
            obj.expiry_date = expiry_date
            obj.save()

        return token

    @classmethod
    def check_token(cls, user, token):
        """
         Check token and return instance or delete it if expired
        """
        try:
            obj = cls.objects.get(user=user, token=token)
        except cls.DoesNotExist:
            return False

        if timezone.now() > obj.expiry_date:
            obj.delete()

            return False

        return True

    @classmethod
    def get_token(cls, user, token):
        try:
            obj = cls.objects.get(user=user, token=token)
        except cls.DoesNotExist:
            return False

        return obj

