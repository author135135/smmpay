from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.flatpages.models import FlatPage
from django.contrib.flatpages.admin import FlatPageAdmin
from .models import Menu, MenuItem, Discussion, Advert, AdvertSocialAccount, Category, Region, SocialNetwork, Phrase
from .forms import AdvertFlatpageForm


class MenuItemInline(admin.StackedInline):
    model = MenuItem


class MenuAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'pages_count')
    inlines = (MenuItemInline,)

    def pages_count(self, obj):
        return obj.menu_items.count()


class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'menu', 'url')


class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('__str__', '_get_users', 'created')

    def _get_users(self, obj):
        return ', '.join([str(user) for user in obj.users.all()])
    _get_users.short_description = _('users')


class AdvertSocialAccountInline(admin.StackedInline):
    model = AdvertSocialAccount


class AdvertAdmin(admin.ModelAdmin):
    inlines = (AdvertSocialAccountInline,)


class CategoryAdmin(admin.ModelAdmin):
    pass


class RegionAdmin(admin.ModelAdmin):
    pass


class SocialNetworkAdmin(admin.ModelAdmin):
    pass


class PhraseAdmin(admin.ModelAdmin):
    pass


class AdvertFlatPageAdmin(FlatPageAdmin):
    form = AdvertFlatpageForm


admin.site.register(Menu, MenuAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(Advert, AdvertAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(SocialNetwork, SocialNetworkAdmin)
admin.site.register(Phrase, PhraseAdmin)

admin.site.unregister(FlatPage)
admin.site.register(FlatPage, AdvertFlatPageAdmin)