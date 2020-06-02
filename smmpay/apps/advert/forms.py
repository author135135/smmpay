import requests
import logging
import os

from urllib.parse import urlparse, urlunparse

from django import forms
from django.core.files.base import ContentFile
from django.core import validators
from django.contrib.flatpages.forms import FlatpageForm
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.translation import get_language_from_request
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .models import (Advert, AdvertSocialAccount, AdvertSocialAccountService, SocialNetwork, SocialNetworkService,
                     Category, ContentBlock, Phrase)
from .widgets import SelectWithOptionAttrs
from .validators import validate_image_file_mime_type

logger = logging.getLogger('db')


class FilterForm(forms.Form):
    SORT_CHOICES = (
        ('-social_account__subscribers', {'label': _('subscribers'),
                                          'data-imagesrc': static('smmpay/images/sort_higher.png')}),
        ('social_account__subscribers', {'label': _('subscribers'),
                                         'data-imagesrc': static('smmpay/images/sort_lower.png')}),
        ('-price', {'label': _('price min'), 'data-imagesrc': static('smmpay/images/sort_higher.png')}),
        ('price', {'label': _('price min'), 'data-imagesrc': static('smmpay/images/sort_lower.png')}),
        ('-views', _('popularity')),
    )

    search_query = forms.CharField(label=_('Search'), required=False, widget=forms.TextInput(
        attrs={'class': 'filter__search', 'placeholder': _("For example 'sport'")}))
    category = forms.MultipleChoiceField(label=_('Category'), required=False, widget=forms.SelectMultiple(
        attrs={'multiple': 'multiple'}))
    service = forms.MultipleChoiceField(label=_('Advertising services'), required=False, widget=forms.SelectMultiple(
        attrs={'multiple': 'multiple'}))
    price = forms.IntegerField(label=_('Price, from'), required=False,
                               widget=forms.TextInput(attrs={'class': 'filter__value'}))
    subscribers_min = forms.IntegerField(label=_('Subscribers, from'), required=False,
                                         widget=forms.TextInput(attrs={'class': 'filter__value'}))
    subscribers_max = forms.IntegerField(label=_('Subscribers, to'), required=False,
                                         widget=forms.TextInput(attrs={'class': 'filter__value'}))
    sort_by = forms.ChoiceField(label=_('Sort by'), required=False, choices=SORT_CHOICES, initial=SORT_CHOICES[0][0],
                                widget=SelectWithOptionAttrs(attrs={'class': 'filter__select', 'id': 'sort_by'}))

    def __init__(self, selected_social_network, *args, **kwargs):
        super(FilterForm, self).__init__(*args, **kwargs)

        self.fields['category'].choices = Category.objects.values_list('slug', 'title')

        if selected_social_network is not None:
            self.fields['service'].choices = SocialNetworkService.objects.filter(
                social_network=selected_social_network).values_list('pk', 'title')


class AdvertSocialAccountServiceForm(forms.ModelForm):
    class Meta:
        fields = ('social_network_service', 'price', 'negotiated_price')
        help_texts = {
            'social_network_service': _('Now you can enter the price for a specific service')
        }
        labels = {
            'social_network_service': _('Service')
        }

    def __init__(self, post_data, *args, **kwargs):
        super(AdvertSocialAccountServiceForm, self).__init__(*args, **kwargs)

        if 'link' in post_data:
            social_account_link = post_data.get('link')
        elif self.social_account_instance.advert_id is not None:
            social_account_link = self.social_account_instance.link
        else:
            social_account_link = None

        if social_account_link:
            social_network = SocialNetwork.get_social_network(social_account_link)
            self.fields['social_network_service'].queryset = SocialNetworkService.objects.filter(
                social_network=social_network)
        else:
            self.fields['social_network_service'].queryset = SocialNetworkService.objects.none()

        for field in self.fields:
            if field != 'negotiated_price':
                self.fields[field].widget.attrs['class'] = 'log__input'

    def validate_unique(self):
        """Removed unique validation because in formset `AdvertSocialAccountServiceFormSet` we made it"""
        pass

    def clean(self):
        cleaned_data = super(AdvertSocialAccountServiceForm, self).clean()

        price = cleaned_data.get('price', None)
        negotiated_price = cleaned_data.get('negotiated_price', None)

        if not price and not negotiated_price:
            self.add_error('price', forms.ValidationError(_('This field is required.'), code='required'))


class AdvertSocialAccountServiceFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(AdvertSocialAccountServiceFormSet, self).__init__(*args, **kwargs)

        self.form.social_account_instance = self.instance

    def validate_unique(self):
        services = []

        for form in self.forms:
            for field_name in form.fields:
                field_value = form.cleaned_data.get(field_name, None)

                if field_name == 'social_network_service' and field_value is not None \
                   and form.cleaned_data['DELETE'] is False:
                    if field_value not in services:
                        services.append(field_value)
                    else:
                        form.add_error(field_name, forms.ValidationError(_('This value already selected'),
                                                                         code='required'))

    def save(self, commit=True):
        for item in self.cleaned_data:
            if item and item['id'] is not None and ((item['DELETE'] is False
               and item['id'].social_network_service != item['social_network_service']) or (item['DELETE'] is True)):
                item['id'].delete()

        super(AdvertSocialAccountServiceFormSet, self).save(commit)


AdvertServiceFormSetFactory = forms.inlineformset_factory(AdvertSocialAccount, AdvertSocialAccountService,
                                                          AdvertSocialAccountServiceForm,
                                                          formset=AdvertSocialAccountServiceFormSet, extra=1,
                                                          can_delete=True, min_num=1, validate_min=True)


class AdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = ('title', 'description', 'price', 'advert_type', 'category', 'for_sale')
        widgets = {
            'advert_type': forms.HiddenInput()
        }
        help_texts = {
            'price': _('Enter the price of the minimum service on your site'),
            'category': _('Select category'),
            'description': _('Add a description of your site, indicate the benefits'),
            'for_sale': _('I will consider buying my site')
        }

    def __init__(self, *args, **kwargs):
        super(AdvertForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            if field != 'for_sale':
                self.fields[field].widget.attrs['class'] = 'log__input'


class AdvertSocialAccountForm(forms.ModelForm):
    logo = forms.FileField(label=_('Logo'), required=False, widget=forms.FileInput(),
                           validators=[validate_image_file_mime_type])
    external_logo = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = AdvertSocialAccount
        fields = ('link', 'subscribers', 'logo')
        widgets = {
            'link': forms.URLInput(attrs={'autofocus': ''})
        }
        help_texts = {
            'link': _('Paste a link to a page, group or channel')
        }
        error_messages = {
            'link': {
                'invalid': _('You have inserted an incorrect value for the link to the page, '
                             'group or account that you are selling *')
            }
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')

        super(AdvertSocialAccountForm, self).__init__(*args, **kwargs)

        for field in self.fields:
            class_name = 'load-avatar-img' if field == 'logo' else 'log__input'

            self.fields[field].widget.attrs['class'] = class_name

    def clean_external_logo(self):
        external_logo_url = self.cleaned_data['external_logo']
        external_logo = None

        if not self.files and external_logo_url:
            try:
                validators.URLValidator(external_logo_url)

                url_info = urlparse(external_logo_url)

                if not url_info.path:
                    raise forms.ValidationError('Incorrect image URL')

                filename = os.path.basename(url_info.path)
            except Exception as e:
                self.add_error('logo', forms.ValidationError(_('Can not download logo automatically,'
                                                               'please select it manually'), code='required'))
                logger.exception(e)

                return external_logo

            try:
                response = requests.get(external_logo_url)

                if response.status_code != 200:
                    raise Exception('Unsupported HTTP response code: {}'.format(response.status_code))

                external_logo = ContentFile(response.content, os.path.basename(filename))
                external_logo._origin_name = external_logo.name

                validate_image_file_mime_type(external_logo)
            except Exception as e:
                self.add_error('logo', forms.ValidationError(_('Can not download logo automatically,'
                                                               'please select it manually'), code='required'))
                logger.exception(e)

        return external_logo

    def clean_link(self):
        social_account_link = self.cleaned_data['link']

        url_info = urlparse(social_account_link)

        return urlunparse((url_info.scheme, url_info.netloc, url_info.path, url_info.params, '', ''))

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

        if social_account.pk is None or 'link' in self.changed_data:
            if social_account.pk is None:
                phrase_obj = Phrase.get_rand_phrase(get_language_from_request(self.request))

                if phrase_obj is not None:
                    social_account.confirmation_code = phrase_obj.phrase
                else:
                    social_account.confirmation_code = get_random_string(length=32)

            social_account_confirm_link = self.request.session.get('social_account_confirm_link', None)
            social_account_confirm_status = self.request.session.get('social_account_confirm_status', None)

            if (social_account_confirm_link is not None and social_account_confirm_status is not None and
                    social_account.link == social_account_confirm_link):
                social_account.confirmed = bool(social_account_confirm_status)
            else:
                social_account.confirmed = False

        if commit:
            social_account.save()

            if 'social_account_confirm_link' in self.request.session:
                del self.request.session['social_account_confirm_link']
            if 'social_account_confirm_status' in self.request.session:
                del self.request.session['social_account_confirm_status']
        return social_account


class AdvertFlatpageForm(FlatpageForm):
    class Meta(FlatpageForm.Meta):
        widgets = {
            'content': CKEditorUploadingWidget()
        }


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


class AdminAdvertForm(forms.ModelForm):
    class Meta:
        model = Advert
        fields = '__all__'
        widgets = {
            'special_status': forms.Select(choices=Advert.ADVERT_SPECIAL_STATUSES)
        }

    def clean(self):
        cleaned_data = super(AdminAdvertForm, self).clean()

        if cleaned_data['special_status'] != Advert.ADVERT_SPECIAL_STATUS_NONE:
            if not self.has_error('special_status_start') and not cleaned_data['special_status_start']:
                self.add_error('special_status_start', forms.ValidationError('This field is required', code='required'))
            if not self.has_error('special_status_end') and not cleaned_data['special_status_end']:
                self.add_error('special_status_end', forms.ValidationError('This field is required', code='required'))


"""
class DiscussionMessageForm(forms.Form):
    message = forms.CharField(label=_('Message'), widget=forms.Textarea(attrs={'placeholder': _('Your message'),
                                                                               'autofocus': ''}))

    def clean_message(self):
        message = self.cleaned_data['message']
        message = message.strip()

        if len(message) == 0:
            raise forms.ValidationError(_('Please enter a message'), code='invalid')
        return message
"""
