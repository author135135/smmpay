from django.contrib import admin
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _

from .models import (Menu, MenuItem, Discussion, DiscussionUser, DiscussionMessage, Advert, AdvertSocialAccount,
                     Category, Region, SocialNetwork, Phrase, SocialAccountConfirmationQueue)
from .forms import AdvertFlatpageForm


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


class AdvertAdmin(admin.ModelAdmin):
    list_display = ('title', 'advert_type', 'category', 'author', 'price', 'enabled_by_author', 'status')
    list_per_page = 20
    search_fields = ('title', 'description')
    list_filter = ('advert_type', 'category', 'enabled_by_author', 'status')
    inlines = (AdvertSocialAccountInline,)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', '_adverts_count')
    list_per_page = 20
    search_fields = ('title',)

    def _adverts_count(self, obj):
        return obj.adverts.count()
    _adverts_count.short_description = _('adverts count')


class RegionAdmin(admin.ModelAdmin):
    list_display = ('title', '_adverts_count')
    list_per_page = 20
    search_fields = ('title',)

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

    def _get_advert(self, obj):
        return obj.social_account.advert
    _get_advert.short_description = _('advert')


class AdvertFlatPageAdmin(FlatPageAdmin):
    form = AdvertFlatpageForm


admin.site.register(Menu, MenuAdmin)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Advert, AdvertAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(SocialNetwork, SocialNetworkAdmin)
admin.site.register(Phrase, PhraseAdmin)
admin.site.register(SocialAccountConfirmationQueue, SocialAccountConfirmationQueueAdmin)

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, AdvertFlatPageAdmin)
