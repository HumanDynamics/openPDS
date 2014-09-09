from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from oms_pds.meetup.views import meetup_home

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('oms_pds.visualization.views',
    (r'^socialHealthRadial', direct_to_template, { 'template' : 'visualization/socialHealthRadial.html' }),
    (r'^activity', direct_to_template, { 'template' : 'visualization/activity.html' }),
    (r'^social', direct_to_template, { 'template' : 'visualization/social.html' }),
    (r'^focus', direct_to_template, { 'template' : 'visualization/focus.html' }),
    (r'^places', "places"),
    (r'^meetup_home', meetup_home),
    (r'^probe_counts', direct_to_template, { 'template': 'visualization/probeCounts.html'}),
#    (r"^places", direct_to_template, { "template" : "visualization/locationMap.html" })
    (r'^mitfit/userlocation$', direct_to_template, { 'template' : 'visualization/mitfit_user_location.html' }),
    (r'^mitfit/usertime$', direct_to_template, { 'template' : 'visualization/mitfit_user_time.html' }),
    (r'^mitfit/statsuser$', direct_to_template, { 'template' : 'visualization/mitfit_stats_user.html' }),
    (r'^mitfit/statsaggregate$', direct_to_template, { 'template' : 'visualization/mitfit_stats_aggregate.html' }),
    (r'^mitfit/recos$', direct_to_template, { 'template' : 'visualization/mitfit_recos.html' }),

    (r'^smartcatch/splash', direct_to_template, { 'template': 'visualization/smartcatch_splash.html'}),
    (r'^smartcatch/myresults', direct_to_template, { 'template': 'visualization/smartcatch_myresults.html'}),
    (r'^smartcatch/history', direct_to_template, { 'template': 'visualization/smartcatch_history.html'}),
    (r'^smartcatch/questions', direct_to_template, { 'template': 'visualization/smartcatch_questions.html'}),
)
