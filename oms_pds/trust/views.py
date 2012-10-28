from django.http import HttpResponse
import json
from django.template import RequestContext
from django.shortcuts import render_to_response
import httplib
from django import forms
import json
from oms_pds.forms.settingsforms import PermissionsForm, Purpose_Form
from oms_pds.pds.models import Scope, Purpose, Role, SharingLevel



def add(request):
    form = Purpose_Form()
    template = {"form":form}

    if request.META.get('CONTENT_TYPE') == 'application/json' or request.GET.get('format') == "json":
        response_dict = {}
        scope_dict = {}
        for s in Scope.objects.all():
            scope_dict.update({s.name:s.name})
        response_dict['scope'] = scope_dict
        role_dict = {}
        for r in Role.objects.all():
            role_dict.update({r.name:r.name})
        response_dict['role'] = role_dict
        sl_dict = {}
        for sl in SharingLevel.objects.all():
            sl_dict.update({sl.level:sl.level})
        response_dict['sharing_level'] = sl_dict

        return HttpResponse(json.dumps(response_dict), content_type='application/json')

    return render_to_response('trust/add.html',
        template,
        RequestContext(request))


