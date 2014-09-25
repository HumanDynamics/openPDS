#-*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url
import logging, random, hashlib, string

urlpatterns = patterns('openpds.connectors.funf.views',
    (r'^set_funf_data$',                 'data'),
#    (r'^set_funf_key$',                 'write_key'),
#    (r'^journal$',                 'journal'),
#    (r'^install_journal$',                 'install_journal'),
#    (r'^config$',                 'config'),
#    (r'^setup$',                 'setup'),

)

