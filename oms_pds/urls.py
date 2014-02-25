from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.contrib import admin
from oms_pds.pds.models import Role, Profile, Purpose, Scope, SharingLevel
from oms_pds.views import federated_sparql_proxy
admin.autodiscover()
admin.site.register(Role)
admin.site.register(Profile)
admin.site.register(Purpose)
admin.site.register(Scope)
admin.site.register(SharingLevel)


#from tastypie.api import Api
#from oms_pds.pds.api import FunfResource, FunfConfigResource, RoleResource, PurposeResource, SocialHealthResource, RealityAnalysisResource
#
#v1_api = Api(api_name='personal_data')
#v1_api.register(FunfResource())
#v1_api.register(FunfConfigResource())
#v1_api.register(RoleResource())
#v1_api.register(PurposeResource())
#v1_api.register(SocialHealthResource())
#v1_api.register(RealityAnalysisResource())

from oms_pds.pds.tools import v1_api
#v1_api.register(SharingResource())

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

from oms_pds.pds.api import AuditEntryResource

audit_entry_resource = AuditEntryResource()

urlpatterns = patterns('oms_pds.views',
    (r'^home/', 'home'),
    (r'^api/', include(v1_api.urls)),
    (r'^discovery/', include('oms_pds.discovery.urls')),
    (r'^purpose/', 'purpose'), 
    (r'^trust/', include('oms_pds.trust.urls')),
    (r'^sharing/', include('oms_pds.sharing.urls')),
    (r'^pdssettings/', 'permissions'), 
    (r'^trustsettings/', 'permissions'),
    (r'^admin/audit', direct_to_template, { 'template' : 'audit.html' }),
    #(r'^documentation/', include('tastytools.urls'), {'api_name': v1_api.api_name}),
    (r'^admin/roles', direct_to_template, { 'template' : 'roles.html' }),
    (r'^admin/', include(admin.site.urls)),
    (r'visualization/', include('oms_pds.visualization.urls')),
    (r'^(?P<owner_uuid>\b[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b)$', "personalProfileRdf"),
    (r"^(?P<owner_uuid>\b[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b)/sparql$", federated_sparql_proxy),
    (r'^funf_connector/', include('oms_pds.funf_connector.urls')),
    (r'^survey/', direct_to_template, { 'template' : 'survey.html' }),
    # Examples:
    # url(r'^$', 'OMS_PDS.views.home', name='home'),
    # url(r'^OMS_PDS/', include('OMS_PDS.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
	
    (r'^funfSetting/', 'funfSetting'),
    (r'^checkboxes/', direct_to_template, { 'template' : 'multiplecheckboxes.html' }),
)
