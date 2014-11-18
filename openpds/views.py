from django.http import HttpResponse, HttpResponseRedirect
import os
import json
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import settings
import httplib
from django import forms
import json
import pdb
from django.templatetags.static import static


def home(request):
    template = {}

    return render_to_response('home.html',
        template,
        RequestContext(request))
    
def ping(request):
    response = {"success":True}
    return HttpResponse(json.dumps(response), mimetype="application/json")

def lab_information(request):
    labs = [
        {
            'name': 'Social Health Tracker',
            'icon': '/static/img/star_1.png',
            'visualizations' : [
                {'title': 'My Social Health', 'key': 'socialHealthRadial', 'answers': ['socialhealth'] },
                {'title': 'Activity', 'key': 'activity', 'answers': ['recentActivityByHour'] },
                {'title': 'Social', 'key': 'social', 'answers': ['recentSocialByHour'] },
                {'title': 'Focus', 'key': 'focus', 'answers': ['recentFocusByHour'] }
            ],
            'answers': [
                { 'key': 'socialhealth', 'data': ['recentActivityByHour', 'recentSocialByHour', 'recentFocusByHour'], 'purpose': ['Social health radial'] },
                { 'key': 'recentActivityByHour', 'data': ['Activity Probe'], 'purpose': ['Social health radial', 'Activity graph'] },
                { 'key': 'recentSocialByHour', 'data': ['Sms Probe', 'Call Log Probe', 'Bluetooth Probe'], 'purpose': ['Social health radial', 'Social graph'] },
                { 'key': 'recentFocusByHour', 'data': ['Screen Probe'], 'purpose': ['Social health radial', 'Focus graph'] }
            ],
            'about': 'Social Health Tracker is an application to construct 3 social health metrics of an individual: activity, social, and focus.',
            'credits': 'Brian Sweatt',
        },
        {
            'name': 'My Places',
            'icon': '/static/img/star_1.png',
            'visualizations': [
                {'title': 'Home / Work', 'key': 'places', 'answers': ['recentPlaces'] }
            ],
            'answers': [
                { 'key': 'recentPlaces', 'data': [ 'Simple Location Probe' ], 'purpose': ['Map'] }
            ],
            'about': 'My Places is an application to mine frequently-visited locations and identify work and home locations.',
            'credits': 'Brian Sweatt'
        },
        {
            'name': 'Meetup',
            'icon': '/static/img/star_1.png',
            'visualizations': [
                {'title': 'Meetup Home', 'key': 'meetup_home', 'answers': ['recentPlaces'] }
            ],
            'about': 'Meetup is an application to enable people schedule meetups without explicitly sharing their location or points of interest.',
            'credits': 'Brian Sweatt, Sharon Paradesi, Ilaria Liccardi'
        },
        {
            'name': 'MIT-FIT',
            'icon': '/static/img/star_1.png',
            'visualizations': [
                {'title': 'High-activity Locations', 'key': 'mitfit/userlocation', 'answers': ['activeLocations'] },
                {'title': 'High-activity Times', 'key': 'mitfit/usertime', 'answers': ['activeLocations'] },
                {'title': 'Your Recommendations', 'key': 'mitfit/recos', 'answers': ['activityStats'] }
            ],
            'answers': [
                { 'key': 'activeLocations', 'data': ['Activity Probe', 'Simple Location Probe'], 'purpose': ['Heatmaps'] },
                { 'key': 'activityStats', 'data': ['Activity Probe', 'Simple Location Probe'], 'purpose': ['Heatmaps', 'Recommendations'] }
            ],
            'about': 'MIT-FIT enables users to track personal and aggregate high-activity regions and times, as well as view personalized fitness-related event recommendations.',
            'credits': 'This lab was developed as part of the big data initiative at MIT led by Prof. Sam Madden and Elizabeth Bruce. The MIT-FIT lab was developed by Sharon Paradesi under the guidance of Dr. Lalana Kagal and with the help of Brian Sweatt. User experience and design suggestions were provided by Myra Hope Eskridge and Laura Watts.'
        },
        {
            'name': 'Beaverdash',
            'icon': '/static/img/star_1.png',
            'visualizations': [
                {'title': 'High-activity Locations', 'key': 'http://bd.ljh.me', 'answers': [] },
            ],
            'answers': [
            ],
            'about': 'MIT-FIT enables users to track personal and aggregate high-activity regions and times, as well as view personalized fitness-related event recommendations.',
            'credits': 'This lab was developed as part of the big data initiative at MIT led by Prof. Sam Madden and Elizabeth Bruce. The MIT-FIT lab was developed by Sharon Paradesi under the guidance of Dr. Lalana Kagal and with the help of Brian Sweatt. User experience and design suggestions were provided by Myra Hope Eskridge and Laura Watts.'
        },
    ]
    json_labs = json.dumps(labs)
    return HttpResponse(json_labs, mimetype="application/json")