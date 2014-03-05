from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from oms_pds.meetup.views import add_approved_participant, contribute_to_scheduling, request_meetup

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('oms_pds.meetup.views',
    (r'^request_meetup', request_meetup),
    (r'^add_approval', add_approved_participant),
    (r'^help_schedule', contribute_to_scheduling),
)

