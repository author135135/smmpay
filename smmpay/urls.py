from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.conf import settings
from django.views.i18n import javascript_catalog

urlpatterns = [
    url(r'^jsi18n/$', javascript_catalog, name='javascript-catalog'),
    url(r'^blog/', include('smmpay.apps.blog.urls', namespace='blog')),
    url(r'^account/', include('smmpay.apps.account.urls', namespace='account')),
    url(r'^forstaffonly/', include(admin.site.urls)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^', include('smmpay.apps.advert.urls', namespace='advert')),
]


if settings.DEBUG:
    try:
        import debug_toolbar

        urlpatterns += [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
