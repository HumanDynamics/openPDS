from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
#from oms_pds.meetup.views import update_approval_status, contribute_to_scheduling, create_request, meetup_home
from oms_pds.accesscontrol.views import storeSettings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('oms_pds.accesscontrol.views',
    (r'^store/$', storeSettings),
)

