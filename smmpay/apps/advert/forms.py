import requests
import logging
import os

from django import forms
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.contrib.flatpages.forms import FlatpageForm
from django.utils.translation import ugettext_lazy as _
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Advert, AdvertSocialAccount, SocialNetwork, Region, Category


class FilterForm(forms.Form):
    search_query = forms.CharField(required=False, label=_('Search'), widget=forms.TextInput(
        attrs={'class': 'filter__search', 'placeholder': _("For example 'sport'")}))
    region = forms.ChoiceField(required=False, label=_('Region'))
    category = forms.ChoiceField(required=False, label=_('Category'))
    price_min = forms.CharField(required=False, label=_('From'),
                                widget=forms.TextInput(attrs={'class': 'filter__value'}))
    price_max = forms.CharField(required=False, label=_('To'), widget=forms.TextInput(attrs={'class': 'filter__value'}))
    subscribers_min = forms.CharField(required=False, label=_('From'),
                                      widget=forms.TextInput(attrs={'class': 'filter__value'}))
    subscribers_max = forms.CharField(required=False, label=_('To'),
                                      widget=forms.TextInput(attrs={'class': 'filter__value'}))

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        region_choices = list(Region.objects.values_list('id', 'title'))
        region_choices.insert(0, [None, _('Any')])

        self.fields['region'].choices = region_choices

        category_choices = list(Category.objects.values_list('id', 'title'))
        category_choices.insert(0, [None, _('Any')])

        self.fields['category'].choices = category_choices


class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ('title', 'description', 'price', 'advert_type')
        widgets = {
            'advert_type': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'placeholder': _('Group for sell...')})
        }
        help_texts = {
            'description': _('Description, use useful information to attract users (1-1000 characters)')
        }

    def __init__(self, *args, **kwargs):
        super(AdvertForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'log__input'


class AdvertSocialAccountAddForm(forms.ModelForm):
    logo = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = AdvertSocialAccount
        fields = ('link', 'subscribers', 'category', 'region')
        help_texts = {
            'link': _('Paste a link to the page, group or account that you are selling *')
        }
        error_messages = {
            'link': {
                'invalid': _('You have inserted an incorrect value for the link to the page, '
                             'group or account that you are selling *')
            }
        }

    def __init__(self, *args, **kwargs):
        super(AdvertSocialAccountAddForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'log__input'

    def clean_link(self):
        link = self.cleaned_data['link']
        social_network = AdvertSocialAccount.get_social_network(link)

        if social_network is None:
            raise forms.ValidationError(_('Unsupported social network'), code='invalid')

        return link

    def save(self, commit=True):
        social_account = super(AdvertSocialAccountAddForm, self).save(commit=False)

        social_network = AdvertSocialAccount.get_social_network(link=social_account.link)

        social_account.social_network = SocialNetwork.objects.get(code=social_network)

        logo_url = self.cleaned_data['logo']

        if logo_url:
            try:
                response = requests.get(logo_url)
            except requests.HTTPError as e:
                logging.exception(e)

            if response.status_code == 200:
                tmp_file = NamedTemporaryFile()
                tmp_file.write(response.content)
                tmp_file.flush()

                social_account.logo.save(os.path.basename(logo_url), File(tmp_file), False)

        if commit:
            social_account.save()
        return social_account


class AdvertSocialAccountEditForm(AdvertSocialAccountAddForm):
    class Meta(AdvertSocialAccountAddForm.Meta):
        fields = ('link', 'subscribers', 'category', 'region')


class AdvertFlatpageForm(FlatpageForm):
    class Meta(FlatpageForm.Meta):
        widgets = {
            'content': CKEditorUploadingWidget()
        }


class DiscussionMessageForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={'placeholder': _('Your message')}))

    def clean_message(self):
        message = self.cleaned_data['message']
        message = message.strip()

        if len(message) == 0:
            raise forms.ValidationError(_('Please enter a message'), code='invalid')
        return message
