import requests
import logging
import os

from django import forms
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core import validators
from django.contrib.flatpages.forms import FlatpageForm
from django.utils.translation import ugettext_lazy as _
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import Advert, AdvertSocialAccount, SocialNetwork, Region, Category, ContentBlock


logger = logging.getLogger('db')


class FilterForm(forms.Form):
    search_query = forms.CharField(label=_('Search'), required=False, widget=forms.TextInput(
        attrs={'class': 'filter__search', 'placeholder': _("For example 'sport'"), 'autofocus': ''}))
    region = forms.ChoiceField(label=_('Region'), required=False)
    category = forms.ChoiceField(label=_('Category'), required=False)
    price_min = forms.IntegerField(label=_('From'), required=False,
                                   widget=forms.TextInput(attrs={'class': 'filter__value'}))
    price_max = forms.IntegerField(label=_('To'), required=False,
                                   widget=forms.TextInput(attrs={'class': 'filter__value'}))
    subscribers_min = forms.IntegerField(label=_('From'), required=False,
                                         widget=forms.TextInput(attrs={'class': 'filter__value'}))
    subscribers_max = forms.IntegerField(label=_('To'), required=False,
                                         widget=forms.TextInput(attrs={'class': 'filter__value'}))

    def __init__(self, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        region_choices = list(Region.objects.values_list('slug', 'title'))
        region_choices.insert(0, [None, _('Any')])

        self.fields['region'].choices = region_choices

        category_choices = list(Category.objects.values_list('slug', 'title'))
        category_choices.insert(0, [None, _('Any')])

        self.fields['category'].choices = category_choices


class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ('title', 'description', 'price', 'advert_type', 'category')
        widgets = {
            'advert_type': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'placeholder': _('Short description')})
        }
        help_texts = {
            'description': _('Description, use useful information to attract users (1-1000 characters)')
        }

    def __init__(self, *args, **kwargs):
        super(AdvertForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'log__input'


class AdvertSocialAccountForm(forms.ModelForm):
    logo = forms.ImageField(label=_('Logo'), required=False, widget=forms.FileInput())
    external_logo = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = AdvertSocialAccount
        fields = ('link', 'subscribers', 'region', 'logo')
        widgets = {
            'link': forms.URLInput(attrs={'autofocus': ''})
        }
        help_texts = {
            'link': _('Paste a link to the page, group or account that you are selling')
        }
        error_messages = {
            'link': {
                'invalid': _('You have inserted an incorrect value for the link to the page, '
                             'group or account that you are selling *')
            }
        }

    def __init__(self, *args, **kwargs):
        super(AdvertSocialAccountForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            class_name = 'load-avatar-img' if field == 'logo' else 'log__input'

            self.fields[field].widget.attrs['class'] = class_name

    def clean_external_logo(self):
        external_logo_url = self.cleaned_data['external_logo']
        external_logo = None

        if external_logo_url:
            try:
                validators.URLValidator(external_logo_url)
            except Exception as e:
                self.add_error('logo', forms.ValidationError(_('Can not download logo automatically,'
                                                               'please select it manually'), code='required'))
                logger.exception(e)

                return external_logo

            try:
                response = requests.get(external_logo_url)

                if response.status_code == 200:
                    tmp_file = NamedTemporaryFile()
                    tmp_file.write(response.content)
                    tmp_file.flush()

                    external_logo = File(tmp_file)
                    external_logo._origin_name = os.path.basename(external_logo_url)
            except Exception as e:
                self.add_error('logo', forms.ValidationError(_('Can not download logo automatically,'
                                                               'please select it manually'), code='required'))
                logger.exception(e)

        return external_logo

    def clean(self):
        cleaned_data = super(AdvertSocialAccountForm, self).clean()

        external_logo_url = cleaned_data.get('external_logo')
        logo = cleaned_data.get('logo')

        if not any([external_logo_url, logo]) and not self.has_error('logo'):
            self.add_error('logo', forms.ValidationError(_('This field is required.'), code='required'))

    def save(self, commit=True):
        social_account = super(AdvertSocialAccountForm, self).save(commit=False)

        social_network = SocialNetwork.get_social_network(link=social_account.link)
        social_account.social_network = social_network

        external_logo = self.cleaned_data['external_logo']

        if external_logo:
            social_account.logo.save(external_logo._origin_name, external_logo, False)

        if commit:
            social_account.save()
        return social_account


class AdvertFlatpageForm(FlatpageForm):
    class Meta(FlatpageForm.Meta):
        widgets = {
            'content': CKEditorUploadingWidget()
        }


class DiscussionMessageForm(forms.Form):
    message = forms.CharField(label=_('Message'), widget=forms.Textarea(attrs={'placeholder': _('Your message'),
                                                                               'autofocus': ''}))

    def clean_message(self):
        message = self.cleaned_data['message']
        message = message.strip()

        if len(message) == 0:
            raise forms.ValidationError(_('Please enter a message'), code='invalid')
        return message


class ContentBlockForm(forms.ModelForm):
    class Meta(FlatpageForm.Meta):
        model = ContentBlock
        fields = '__all__'
        widgets = {
            'content': CKEditorUploadingWidget()
        }

    def clean(self):
        cleaned_data = super(ContentBlockForm, self).clean()

        if not any([cleaned_data['content'], cleaned_data['context_function']]):
            self.add_error('content', forms.ValidationError('Required if `context function` is empty', code='required'))
            self.add_error('context_function', forms.ValidationError('Required if `content` is empty', code='required'))
