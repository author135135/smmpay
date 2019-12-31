from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile

    can_delete = False


class UserAdmin(DefaultUserAdmin):
    list_display = ('email', 'is_admin', 'is_superuser')
    list_per_page = 20
    list_filter = ('is_admin', 'is_superuser')
    inlines = (ProfileInline,)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_admin', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2')}),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def get_inline_instances(self, request, obj=None):
        if obj is None:
            return []
        return super(UserAdmin, self).get_inline_instances(request, obj)


admin.site.register(User, UserAdmin)
