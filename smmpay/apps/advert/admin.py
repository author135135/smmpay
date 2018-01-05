from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from .models import (Menu, MenuItem, Discussion, DiscussionUser, DiscussionMessage, Advert, AdvertSocialAccount,
                     Category, Region, SocialNetwork, Phrase, SocialAccountConfirmationQueue, ContentBlock,
                     VipAdvert, TopAdvert)
from .forms import AdvertFlatpageForm, ContentBlockForm


class MenuItemInline(admin.StackedInline):
    model = MenuItem
    extra = 1


class MenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', '_links_count')
    list_per_page = 20
    inlines = (MenuItemInline,)

    def _links_count(self, obj):
        return obj.menu_items.count()


class DiscussionUserInline(admin.StackedInline):
    model = DiscussionUser
    readonly_fields = ('user',)
    can_delete = False

    def has_add_permission(self, request):
        return False


class DiscussionMessageInline(admin.StackedInline):
    model = DiscussionMessage
    readonly_fields = ('sender', 'message', 'created')
    can_delete = False

    def has_add_permission(self, request):
        return False


class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('advert', '_get_users', '_messages_count', 'created')
    list_per_page = 20
    search_fields = ('advert__title',)
    inlines = (DiscussionUserInline, DiscussionMessageInline)
    readonly_fields = ('advert', 'created')

    def has_add_permission(self, request):
        return False

    def _get_users(self, obj):
        return ', '.join([str(user) for user in obj.discussion_users.all()])
    _get_users.short_description = _('users')

    def _messages_count(self, obj):
        return obj.discussion_messages.count()
    _messages_count.short_description = _('messages')


class AdvertSocialAccountInline(admin.StackedInline):
    model = AdvertSocialAccount


class VipAdvertInline(admin.StackedInline):
    model = VipAdvert


class TopAdvertInline(admin.StackedInline):
    model = TopAdvert


class AdvertAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'advert_type', '_get_social_network', 'author', 'price', 'enabled_by_author',
                    '_get_in_vip', '_get_in_top', 'status')
    list_per_page = 20
    search_fields = ('title', 'description')
    list_filter = ('advert_type', 'category', 'social_account__social_network', 'enabled_by_author', 'status')
    inlines = (AdvertSocialAccountInline, VipAdvertInline, TopAdvertInline)

    def _get_social_network(self, obj):
        return obj.social_account.social_network
    _get_social_network.short_description = _('social network')

    def _get_in_vip(self, obj):
        return obj.in_vip()
    _get_in_vip.short_description = _('in vip')
    _get_in_vip.boolean = True

    def _get_in_top(self, obj):
        return obj.in_top()
    _get_in_top.short_description = _('in top')
    _get_in_top.boolean = True


class MarkedAdvertAdmin(admin.ModelAdmin):
    list_display = ('_get_advert_title', 'date_start', 'date_end')
    list_per_page = 20
    search_fields = ('advert__title', 'advert__description')

    def _get_advert_title(self, obj):
        return obj.advert.title
    _get_advert_title.short_description = _('title')


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', '_adverts_count')
    list_per_page = 20
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

    def _adverts_count(self, obj):
        return obj.adverts.count()
    _adverts_count.short_description = _('adverts count')


class RegionAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', '_adverts_count')
    list_per_page = 20
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

    def _adverts_count(self, obj):
        return obj.social_accounts.count()
    _adverts_count.short_description = _('social accounts count')


class SocialNetworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'order', '_adverts_count')
    list_per_page = 20
    search_fields = ('title',)

    def _adverts_count(self, obj):
        return obj.social_accounts.count()
    _adverts_count.short_description = _('social accounts count')


class PhraseAdmin(admin.ModelAdmin):
    list_display = ('_get_phrase', 'language')
    list_per_page = 20
    search_fields = ('phrase',)
    list_filter = ('language',)

    def _get_phrase(self, obj):
        return Truncator(obj.phrase).words(10)
    _get_phrase.short_description = _('phrase')


class SocialAccountConfirmationQueueAdmin(admin.ModelAdmin):
    list_display = ('_get_advert', 'status', 'attempts', 'last_start')
    list_per_page = 20
    search_fields = ('social_account__advert__title',)
    list_filter = ('status',)

    def _get_advert(self, obj):
        return obj.social_account.advert
    _get_advert.short_description = _('advert')

    def get_queryset(self, request):
        return SocialAccountConfirmationQueue.objects.select_related('social_account__advert')


class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ('title', '_get_pages', 'position', 'enabled')
    list_per_page = 20
    search_fields = ('title',)
    list_filter = ('position', 'enabled')

    form = ContentBlockForm

    def _get_pages(self, obj):
        return '<br>'.join(obj.pages.splitlines())
    _get_pages.short_description = _('pages')
    _get_pages.allow_tags = True


class AdvertFlatPageAdmin(FlatPageAdmin):
    form = AdvertFlatpageForm


admin.site.register(Menu, MenuAdmin)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Advert, AdvertAdmin)
# For now we use one admin model for two models
admin.site.register(VipAdvert, MarkedAdvertAdmin)
admin.site.register(TopAdvert, MarkedAdvertAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(SocialNetwork, SocialNetworkAdmin)
admin.site.register(Phrase, PhraseAdmin)
admin.site.register(SocialAccountConfirmationQueue, SocialAccountConfirmationQueueAdmin)
admin.site.register(ContentBlock, ContentBlockAdmin)

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, AdvertFlatPageAdmin)
