from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.views.decorators.cache import cache_page
from views import groupOverview, patientInfo

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('oms_pds.clinician.views',
                       (r'^group_overview/(?P<status>\w+)$', groupOverview),
                       (r'^patients/(?P<uid>\b[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}\b)$', patientInfo),
)
