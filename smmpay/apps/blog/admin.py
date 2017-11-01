from django.contrib import admin
from .models import Post
from .forms import PostForm


class PostAdmin(admin.ModelAdmin):
    form = PostForm
    fieldsets = (
        (None, {'fields': ('title', 'url', 'content', 'image', 'status')}),
    )
    prepopulated_fields = {'url': ('title',)}
    list_display = ('title', 'status', 'created')
    list_filter = ('status',)
    search_fields = ('title',)


admin.site.register(Post, PostAdmin)
