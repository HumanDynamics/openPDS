from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib import admin
from openpds.core.models import Role, Profile, Purpose, Scope, SharingLevel

admin.autodiscover()
from openpds.core.tools import v1_api
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from openpds.core.api import AuditEntryResource

audit_entry_resource = AuditEntryResource()

urlpatterns = patterns('openpds.views',
    (r'^home/', 'home'),
    (r'^api/', include(v1_api.urls)),
    (r'^admin/audit', direct_to_template, { 'template' : 'audit.html' }),
    #(r'^documentation/', include('tastytools.urls'), {'api_name': v1_api.api_name}),
    (r'^admin/roles', direct_to_template, { 'template' : 'roles.html' }),
    (r'^admin/', include(admin.site.urls)),
    (r'visualization/', include('openpds.visualization.urls')),
    (r'^funf_connector/', include('openpds.connectors.funf.urls')),
    (r'^survey/', direct_to_template, { 'template' : 'survey.html' }),
    (r"meetup/", include("openpds.meetup.urls")),
    # Examples:
    # url(r'^$', 'OMS_PDS.views.home', name='home'),
    # url(r'^OMS_PDS/', include('OMS_PDS.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
	
    #(r'^funfSetting/', 'funfSetting'),
    (r"accesscontrol/", include("openpds.accesscontrol.urls")),
    (r'probevisualization/', direct_to_template, { 'template' : 'probevisualization.html' }),
    (r'^checkboxes/', direct_to_template, { 'template' : 'multiplecheckboxes.html' }),
)
