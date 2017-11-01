from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^(?P<url>[-\w]+)/$', views.PostView.as_view(), name='post'),
]
