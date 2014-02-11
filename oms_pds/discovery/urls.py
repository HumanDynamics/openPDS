#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, url, include

urlpatterns = patterns('oms_pds.discovery.views',
    (r'^ping', 'ping'),
    (r'^members', 'members'),
)


