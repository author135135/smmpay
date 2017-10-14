from django.conf.urls import url
from django.contrib.auth import views as auth_views
from registration.backends.hmac.urls import urlpatterns as register_urlpatterns

from smmpay.settings import LOGOUT_REDIRECT_URL
from . import views
from .forms import AuthenticationForm, PasswordResetForm, SetPasswordForm

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^password-reset/$', auth_views.password_reset,
        {'post_reset_redirect': 'account:password_reset_done',
         'password_reset_form': PasswordResetForm},
        name='password_reset'),
    url(r'^password-reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'post_reset_redirect': 'account:password_reset_complete',
         'set_password_form': SetPasswordForm},
        name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),
    url(r'^registration/$', views.RegistrationView.as_view(), name='registration'),
    url(r'^activate/(?P<activation_key>[-:\w]+)/$', views.ActivationView.as_view(), name='account_activate'),
    url(r'^login/$', auth_views.login, {'authentication_form': AuthenticationForm}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': LOGOUT_REDIRECT_URL}, name='logout'),
    url(r'^offer/(?P<pk>[0-9]+)/deactivate/$', views.AdvertDeactivateView.as_view(), name='advert_deactivate'),
    url(r'^offer/(?P<pk>[0-9]+)/activate/$', views.AdvertActivateView.as_view(), name='advert_activate'),
    url(r'^discussion/$', views.DiscussionsView.as_view(), name='discussions'),
    url(r'^discussion/(?P<pk>[0-9]+)/$', views.DiscussionView.as_view(), name='discussion'),
    url(r'^discussion/(?P<pk>[0-9]+)/add-message/$', views.DiscussionMessageAddView.as_view(),
        name='discussion_add_message'),
    url(r'^discussion/(?P<pk>[0-9]+)/add-views/$', views.DiscussionMessageViewAddView.as_view(),
        name='discussion_add_view'),
    url(r'^favorite/$', views.FavoritesView.as_view(), name='favorites'),
    url(r'^favorite/(?P<pk>[0-9]+)/delete/$', views.FavoriteDeleteView.as_view(), name='favorite_delete'),
    url(r'^settings/$', views.SettingsView.as_view(), name='settings'),
    url(r'^settings/email-change/(?P<token>[0-9A-Za-z]{1,20})$',
        views.EmailChangeConfirmView.as_view(), name='email_change_confirm'),
    url(r'^delete/$', views.AccountDeleteView.as_view(), name='account_delete')

] + register_urlpatterns
