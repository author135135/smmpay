from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^offer/(?P<pk>[0-9]+)/$', views.AdvertView.as_view(), name='advert'),
    url(r'^offer/(?P<pk>[0-9]+)/edit/$', views.AdvertEditView.as_view(), name='advert_edit'),
    # url(r'^offer/(?P<pk>[0-9]+)/send-message/$', views.AdvertSendMessageView.as_view(),
    #     name='send_message'),
    url(r'^offer/(?P<pk>[0-9]+)/add-view/$', views.AdvertAddViewView.as_view(),
        name='add_view'),
    url(r'^offer/add/$', views.AdvertAddView.as_view(), name='advert_add'),
    url(r'^offer/add/social-account/info/$', views.AdvertSocialAccountInfoView.as_view(),
        name='advert_social_account_info'),
    url(r'^offer/add/social-account/services/$', views.AdvertSocialAccountServicesView.as_view(),
        name='advert_social_account_services'),
    url(r'^offer/add/social-account/confirm/$', views.AdvertSocialAccountConfirmView.as_view(),
        name='advert_social_account_confirm'),
    url(r'^favorite/offer/$', views.FavoriteAdvertView.as_view(), name='favorite_advert'),
    # url(r'^user/(?P<pk>[0-9]+)/offer/$', views.UserAdvertsView.as_view(), name='user_adverts'),
    url(r'^(?P<social_network>[\w]+)/$', views.SocialNetworkView.as_view(), name='social_network'),
    url(r'^(?P<social_network>[\w]+)/(?P<service_id>[0-9]+)/$', views.SocialNetworkServiceView.as_view(),
        name='social_network_service'),
]
