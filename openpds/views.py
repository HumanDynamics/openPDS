from django.http import HttpResponse, HttpResponseRedirect
import json
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import settings
import httplib
from django import forms
import json
from openpds.forms.settingsforms import PermissionsForm, Purpose_Form
from openpds.core.models import Scope, Purpose, Role, SharingLevel, Profile, ResourceKey
from pymongo import Connection
import pdb
from fourstore.views import sparql_proxy
import logging
logger = logging.getLogger(__name__)

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

def home(request):
    template = {}
    template = get_datastore_owner(template, request)

    return render_to_response('home.html',
        template,
        RequestContext(request))
    
def ping(request):
    response = {"success":True}
    return HttpResponse(json.dumps(response), mimetype="application/json")
