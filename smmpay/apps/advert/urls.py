from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^advert/(?P<pk>[0-9]+)/$', views.AdvertView.as_view(), name='advert'),
    url(r'^advert/(?P<pk>[0-9]+)/edit/$', views.AdvertEditView.as_view(), name='advert_edit'),
    url(r'^advert/(?P<pk>[0-9]+)/add-to-favorites/$', views.AdvertAddToFavoritesView.as_view(),
        name='add_to_favorites'),
    url(r'^advert/(?P<pk>[0-9]+)/delete-from-favorites/$', views.AdvertDeleteFromFavoritesView.as_view(),
        name='delete_from_favorites'),
    url(r'^advert/(?P<pk>[0-9]+)/send-message/$', views.AdvertSendMessageView.as_view(),
        name='send_message'),
    url(r'^advert/(?P<pk>[0-9]+)/add-view/$', views.AdvertAddViewView.as_view(),
        name='add_view'),
    url(r'^advert/add/$', views.AdvertAddView.as_view(), name='advert_add'),
    url(r'^advert/add/social-account/info/$', views.AdvertSocialAccountInfoView.as_view(),
        name='advert_social_account_info'),
    url(r'^user/(?P<pk>[0-9]+)/adverts/$', views.UserAdvertsView.as_view(), name='user_adverts'),
]
