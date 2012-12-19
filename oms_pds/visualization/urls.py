from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('oms_pds.trust.views',
    (r'^triangle', direct_to_template, { 'template' : 'visualization/socialHealthTriangle.html' }),
)
