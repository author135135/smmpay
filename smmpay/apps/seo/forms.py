from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import PageSeoInformation


class PageSeoInformationAdminForm(forms.ModelForm):
    class Meta:
        model = PageSeoInformation
        fields = '__all__'
        widgets = {
            'meta_description': forms.Textarea(),
            'meta_keywords': forms.Textarea(),
        }

    def clean_page_url(self):
        page_url = self.cleaned_data['page_url']
        page_url = page_url.strip()

        if not page_url.startswith('/') or not page_url.endswith('/'):
            raise forms.ValidationError(_('Please make sure that page url have leading and trailing slashes'),
                                        code='invalid')
        return page_url
