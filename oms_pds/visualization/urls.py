from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('oms_pds.trust.views',
    (r'^socialHealthRadial', direct_to_template, { 'template' : 'visualization/socialHealthRadial.html' }),
    (r'^activity', direct_to_template, { 'template' : 'visualization/activity.html' }),
    (r'^social', direct_to_template, { 'template' : 'visualization/social.html' }),
    (r'^focus', direct_to_template, { 'template' : 'visualization/focus.html' }),
    (r'^places', direct_to_template, { 'template' : 'visualization/locationMap.html' }),

)
