from collections import OrderedDict

from django import forms
from django.template import loader
from django.core.mail import EmailMultiAlternatives
from django.core.validators import RegexValidator
from django.contrib.auth.forms import (
    AuthenticationForm as AuthAuthenticationForm,
    PasswordResetForm as AuthPasswordResetForm,
    SetPasswordForm as AuthSetPasswordForm,
    PasswordChangeForm as AuthPasswordChangeForm
)
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import ugettext_lazy as _

from registration import forms as registration_forms

from .tokens import email_change_token_generator


User = get_user_model()


class AuthenticationForm(AuthAuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'log__input'


class PasswordResetForm(AuthPasswordResetForm):
    def __init__(self, *args, **kwargs):
        super(PasswordResetForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'log__input'

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(_('Email address does not exists'), code='invalid')

        return email


class SetPasswordForm(AuthSetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'log__input'


class RegistrationForm(registration_forms.RegistrationForm):
    first_name = forms.CharField(label=_('First name'), required=True, widget=forms.TextInput(attrs={'autofocus': ''}))

    class Meta(registration_forms.RegistrationForm.Meta):
        model = User
        fields = ['first_name'] + registration_forms.RegistrationForm.Meta.fields

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'log__input'


class ProfileForm(forms.Form):
    first_name = forms.CharField(label=_('First name'), widget=forms.TextInput(attrs={'class': 'log__input'}))
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message=_('Phone number must be entered in the format: +999999999'))
    phone_number = forms.CharField(label=_('Phone number'), required=False, validators=[phone_regex],
                                   widget=forms.TextInput(attrs={'class': 'log__input'}))
    is_profile_public = forms.BooleanField(label=_('Show profile information'), required=False)
    form_type = forms.CharField(widget=forms.HiddenInput, initial='profile_form')

    def __init__(self, user, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        self.user = user

    def save(self, *args, **kwargs):
        self.user.profile.first_name = self.cleaned_data['first_name']
        self.user.profile.phone_number = self.cleaned_data['phone_number']

        self.user.is_profile_public = self.cleaned_data['is_profile_public']

        self.user.save()

        return self.user


class PasswordChangeForm(AuthPasswordChangeForm):
    form_type = forms.CharField(widget=forms.HiddenInput, initial='password_change_form')

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'log__input'

            if 'autofocus' in self.fields[field].widget.attrs:
                del self.fields[field].widget.attrs['autofocus']

    def save(self, *args, **kwargs):
        super(PasswordChangeForm, self).save(True)

        request = kwargs.get('request', None)

        if request is not None:
            update_session_auth_hash(request, self.user)

        return self.user


PasswordChangeForm.base_fields = OrderedDict(
    (k, PasswordChangeForm.base_fields[k])
    for k in ['form_type', 'old_password', 'new_password1', 'new_password2']
)


class EmailChangeForm(forms.Form):
    email = forms.EmailField(label=_('New email'), max_length=254)
    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput())
    form_type = forms.CharField(widget=forms.HiddenInput, initial='email_change_form')

    def __init__(self, request, *args, **kwargs):
        self.request = request

        super(EmailChangeForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'log__input'

    def clean_email(self):
        email = self.cleaned_data['email']

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Email address already in use'), code='invalid')

        return email

    def clean_password(self):
        password = self.cleaned_data['password']

        if not self.request.user.check_password(password):
            raise forms.ValidationError(_('Your password entered incorrect'), code='invalid')

        return password

    def save(self, *args, **kwargs):
        self.change_email(use_https=self.request.is_secure(), request=self.request)

    def change_email(self, subject_template_name='account/email_change_subject.txt',
                     email_template_name='account/email_change_email.html', use_https=False,
                     token_generator=email_change_token_generator, from_email=None, request=None,
                     html_email_template_name=None):

        email = self.cleaned_data['email']

        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        context = {
            'email': email,
            'domain': domain,
            'site_name': site_name,
            'token': token_generator.make_token(request.user, email),
            'protocol': 'https' if use_https else 'http',
        }

        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())

        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [email])

        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()


class SearchForm(forms.Form):
    query = forms.CharField(label=_('Search query'), required=False, widget=forms.TextInput(
        attrs={'class': 'filter__search', 'placeholder': _("For example 'sport'")}))
    order = forms.ChoiceField(label=_('Order'), required=False, widget=forms.Select(attrs={'class': 'filter__select'}))

    def __init__(self, order_choices, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.fields['order'].choices = order_choices


class DiscussionMessageForm(forms.Form):
    message = forms.CharField(label=_('Message'), widget=forms.Textarea(attrs={'placeholder': _('Your message')}))

    def clean_message(self):
        message = self.cleaned_data['message']
        message = message.strip()

        if len(message) == 0:
            raise forms.ValidationError(_('Please enter a message'), code='invalid')
        return message
