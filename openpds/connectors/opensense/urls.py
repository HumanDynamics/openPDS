#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('openpds.connectors.opensense.views',
    (r'^upload$',                 'data'),
    (r'^register$',				'register'),
    #(r'^config$',				'config'),

)

