from django.conf.urls import patterns, url
from trigger import views

urlpatterns = patterns('',
    url(r'^$', views.welcome_view, name='welcome'),
    url(r'^config/$',views.config_view, name='config'),
    url(r'^result/$' , views.result_view, name='result'),
    url(r'^http/$',views.http_view, name='http'),
    url(r'^logout/$',views.logout_view, name = 'logout'),
)
