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
