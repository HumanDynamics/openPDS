from django.http import HttpResponse
import json
from django.template import RequestContext
from django.shortcuts import render_to_response
import settings
import httplib
from django import forms
import json
from oms_pds.forms.settingsforms import PermissionsForm, Purpose_Form
from oms_pds.pds.models import Scope, Purpose, Role, SharingLevel

def purpose(request):
    form = Purpose_Form()
    template = {"form":form}
    template = get_datastore_owner(template, request)

    return render_to_response('purpose.html',
        template,
        RequestContext(request))

def permissions(request):
    form = Purpose_Form()
    template = {"form":form}
    template = get_datastore_owner(template, request)

    if request.META.get('CONTENT_TYPE') == 'application/json' or request.GET.get('format') == "json":
	response_dict = {}
	scope_dict = {} 
	for s in Scope.objects.all(datastore_owner_id=request.GET.get('datastore_owner')):
	    scope_dict.update({s.name:s.name})
	response_dict['scope'] = scope_dict
	role_dict = {} 
	for r in Role.objects.all(datastore_owner_id=request.GET.get('datastore_owner')):
	    role_dict.update({r.name:r.name})
	response_dict['role'] = role_dict
	sl_dict = {} 
	for sl in SharingLevel.objects.all(datastore_owner_id=request.GET.get('datastore_owner')):
	    sl_dict.update({sl.level:sl.level})
	response_dict['sharing_level'] = sl_dict
	    
        return HttpResponse(json.dumps(response_dict), content_type='application/json')

    return render_to_response('permissions.html',
        template,
        RequestContext(request))



def home(request):
    template = {}
    template = get_datastore_owner(template, request)

    return render_to_response('home.html',
        template,
        RequestContext(request))


def get_datastore_owner(template, request):
    if request.GET.get('datastore_owner') == None:
        raise Exception('missing datastore_owner')
    template['datastore_owner']=request.GET.get('datastore_owner')
    return template

