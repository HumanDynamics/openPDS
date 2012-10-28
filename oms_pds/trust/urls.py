from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('oms_pds.trust.views',
    (r'^add/', 'add'),
)
