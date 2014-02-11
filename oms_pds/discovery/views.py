from django.http import HttpResponse
import json
from django.template import RequestContext
from django.shortcuts import render_to_response
from oms_pds.settings import SERVER_OMS_REGISTRY
from oms_pds.trust.models import Role
from django import forms
import json
import requests

def ping(request):
    response = {"success":True}
    return HttpResponse(json.dumps(response), mimetype="application/json")


def members(request):
    roles = Role.objects.all()
    r = requests.get("http://"+SERVER_OMS_REGISTRY+"/discovery/members")
    print r
    template = {}
    template['profiles'] = r.json['profiles']
    template['roles'] = roles
    print template
    return render_to_response('discovery/members.html',
        template,
        RequestContext(request))



