from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from tastypie.api import Api
from oms_pds.pds.api import FunfResource, FunfConfigResource, RoleResource

v1_api = Api(api_name='personal_data')
v1_api.register(FunfResource())
v1_api.register(FunfConfigResource())
v1_api.register(RoleResource())

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),
    # Examples:
    # url(r'^$', 'OMS_PDS.views.home', name='home'),
    # url(r'^OMS_PDS/', include('OMS_PDS.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
