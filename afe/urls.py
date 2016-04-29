from django.conf.urls import patterns, include, url
from django.contrib import admin
from receiver import views

urlpatterns = patterns('',
        url(r'^', include('receiver.urls')),       
        url(r'^django-rq/', include('django_rq.urls')),
        url(r'^admin/', include(admin.site.urls)),
	url('^', include('django.contrib.auth.urls')),
)



