from django.contrib import admin
from django.template.defaultfilters import truncatewords
from django.utils.translation import ugettext_lazy as _

from .models import PageSeoInformation
from .forms import PageSeoInformationAdminForm


class PageSeoInformationAdmin(admin.ModelAdmin):
    list_display = ('page_url', 'meta_title', '_get_meta_description', '_get_meta_keywords')
    list_display_links = ('page_url', 'meta_title')
    search_fields = ('meta_title', 'meta_description', 'meta_keywords')
    list_per_page = 20

    form = PageSeoInformationAdminForm

    def _get_meta_description(self, obj):
        return truncatewords(obj.meta_description, 10)
    _get_meta_description.short_description = _('Meta description')

    def _get_meta_keywords(self, obj):
        return truncatewords(obj.meta_keywords, 10)
    _get_meta_keywords.short_description = _('Meta keywords')

admin.site.register(PageSeoInformation, PageSeoInformationAdmin)
