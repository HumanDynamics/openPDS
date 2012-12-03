from django.http import HttpResponse
import json
from django.template import RequestContext
from django.shortcuts import render_to_response
import httplib
from django import forms
import json
from oms_pds.sharing.forms.settingsforms import Sharing_Form, ProbeGroupSetting
import oms_pds.sharing.forms.settingsforms as settingsforms
#from oms_pds.trust.models import Scope, Purpose, Role, SharingLevel
from oms_pds.pds.models import Scope, Purpose, Role, SharingLevel



def edit(request):
    '''A web interface for modifying trust framework permissions'''
    form = settingsforms.Sharing_Form()
    template = {"form":form}
    if request.GET.get('datastore_owner') == None:
        raise Exception('missing datastore_owner')
    datastore_owner = request.GET.get('datastore_owner')
    template['datastore_owner']=datastore_owner
    form.update_form(datastore_owner)

    probes = ProbeGroupSetting.objects.all()
    roles = Role.objects.filter(datastore_owner_id=datastore_owner)
    sharinglevels = SharingLevel.objects.filter(datastore_owner_id=datastore_owner)
    scopes = Scope.objects.filter(datastore_owner_id=datastore_owner)
 
    try:
        if request.method == "POST":
    	    # Process web form from web permission interface
    	    for json_input in json.loads(request.body):
    	        if json_input.get('name') == 'probes':
    	            pgs = ProbeGroupSetting.objects.get(name=json_input['value'])
		    pgs.issharing = json_input['selected']
    		    pgs.save()
    	        elif json_input.get('name') == 'roles':
    	            role = Role.objects.get(name=json_input['value'], datastore_owner_id=datastore_owner)
		    role.issharing = json_input['selected']
    		    role.save()
    	        elif json_input.get('name') == 'sharinglevel':
    	            sl = SharingLevel.objects.get(level=json_input['value'], datastore_owner_id=datastore_owner)
		    sl.isselected = json_input['selected']
    		    sl.save()

        if request.META.get('CONTENT_TYPE') == 'application/json' or request.GET.get('format') == "json":
            response_dict = {}
            scope_dict = {}
            for s in scopes:
                scope_dict.update({s.name:s.name})
            response_dict['scope'] = scope_dict
            role_dict = {}
            for r in roles:
                role_dict.update({r.name:r.name})
            response_dict['role'] = role_dict
            sl_dict = {}
            for sl in sharinglevels:
                sl_dict.update({sl.level:sl.level})
            response_dict['sharing_level'] = sl_dict

            return HttpResponse(json.dumps(response_dict), content_type='application/json')
    except Exception as e:
	print e
	
    template['probes'] = probes
    template['roles'] = roles
    template['sharinglevels'] = sharinglevels

    return render_to_response('sharing/edit.html',
        template,
        RequestContext(request))


def update(request):
    return render_to_response('sharing/update.html',
        {},
        RequestContext(request))
