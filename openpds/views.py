from django.http import HttpResponse, HttpResponseRedirect
import json
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import settings
import httplib
from django import forms
import json
import pdb

def home(request):
    template = {}

    return render_to_response('home.html',
        template,
        RequestContext(request))
    
def ping(request):
    response = {"success":True}
    return HttpResponse(json.dumps(response), mimetype="application/json")

def lab_information(request):
    labs = ["Social Health Tracker", "My Places", "Meetup", "MIT FIT"]
    lab_info = {"Labs": labs, "Social Health Tracker": ["../static/img/star_1.png", "Keep track of your social activity throughout the day.", "Brian Sweatt"], "My Places": ["../static/img/star_1.png", "Keep track of your most visited places.", "Brian Sweatt"], "Meetup": ["../static/img/star_1.png", "Organize meetups with other people.", "Brian Sweatt"], "MIT FIT": ["../static/img/star_1.png", "MIT FIT is a fitness application.", "Sharon Paradesi"]}
    json_labs = json.dumps(lab_info)
    return HttpResponse(json_labs, mimetype="application/json")