from django.http import HttpResponse, HttpResponseRedirect
import json
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
import settings
import httplib
from django import forms
import json
from oms_pds.forms.settingsforms import PermissionsForm, Purpose_Form
from oms_pds.pds.models import Scope, Purpose, Role, SharingLevel, Profile, ResourceKey
from pymongo import Connection
import pdb
from fourstore.views import sparql_proxy
from oms_pds.accesscontrol.forms import FunfProbeSettingForm
from oms_pds.accesscontrol.models import FunfProbeModel
import logging
logger = logging.getLogger(__name__)

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

def federated_sparql_proxy(request, owner_uuid):
    #pdb.set_trace()
    url = "http://linkedpersonaldata.org:8004/%s" % owner_uuid
    if request.method=="POST":
        request.POST = request.POST.copy()
        request.POST.update({ "default-graph-uri":  url })
    else:
        request.GET = request.GET.copy()
        request.GET.update({ "default-graph-uri":  url })
    request.META = request.META.copy()
    request.META.update({ "CONTENT_TYPE":"application/x-www-form-urlencoded"})
    #pdb.set_trace()
    return sparql_proxy(request, "http://linkedpersonaldata.org:3030")

def purpose(request):
    form = Purpose_Form()
    template = {"form":form}
    template = get_datastore_owner(template, request)

    return render_to_response('purpose.html',
        template,
        RequestContext(request))

def personalProfileRdf(request, owner_uuid):
    try:
        profile = Profile.objects.get(uuid = owner_uuid)
    except ObjectDoesNotExist:
        profile = None

    template = {}
    if profile is not None:
        socialHealthResource, created = ResourceKey.objects.get_or_create(key="SocialHealth", datastore_owner = profile)
        suggestedPlacesResource, created = ResourceKey.objects.get_or_create(key="SuggestedPlaces", datastore_owner = profile)
        musicGenresResource, created = ResourceKey.objects.get_or_create(key="MusicGenres", datastore_owner = profile)
        friendsResource, created = ResourceKey.objects.get_or_create(key="Friends", datastore_owner = profile)
        dbName = "User_" + str(profile.id)
        answerListCollection = connection[dbName]["answerlist"]
        if socialHealthResource.issharing:
            try:
                socialHealthScores = answerListCollection.find({ "key": "socialhealth"})
                socialHealthScores = socialHealthScores[0]["value"] if socialHealthScores.count() > 0 else []
                userScores = { k:v for (k,v) in [(score["key"], score["value"]) for score in socialHealthScores if score["layer"] == "User"]}
                lows = { k:v for (k,v) in [(score["key"], score["value"]) for score in socialHealthScores if score["layer"] == "averageLow"]}
                highs = { k:v for (k,v) in [(score["key"], score["value"]) for score in socialHealthScores if score["layer"] == "averageHigh"]}
                lpdLow = "http://linkedpersonaldata.org/ontology#low"
                lpdAverage = "http://linkedpersonaldata.org/ontology#average"
                lpdHigh = "http://linkedpersonaldata.org/ontology#high"
                template["recentActivityLevel"] = lpdHigh if userScores["activity"] > highs["activity"] else lpdAverage if userScores["activity"] > lows["activity"] else lpdLow
                template["recentSocialLevel"] = lpdHigh if userScores["social"] > highs["social"] else lpdAverage if userScores["social"] > lows["social"] else lpdLow
                template["recentFocusLevel"] = lpdHigh if userScores["focus"] > highs["focus"] else lpdAverage if userScores["focus"] > lows["focus"] else lpdLow
            except Exception:
                print "RDF failed"            
        template["uuid"] = profile.uuid
        if suggestedPlacesResource.issharing:
            try:
                lpd = "http://linkedpersonaldata.org/ontology#near%s"
                nearHome = lpd % "Home"
                nearWork = lpd % "Work"
                suggestedPlaces = answerListCollection.find({ "key": "SuggestedPlaces" })
                suggestedPlaces = suggestedPlaces[0]["value"] if suggestedPlaces.count() > 0 else []
                suggestedPlaces = [ { "uri": place["uri"], "reason": nearWork if "work" in place["reason"].lower() else nearHome } for place in suggestedPlaces]
                template["suggestedPlaces"] = suggestedPlaces
            except Exception as ex:
                print "RDF failed"
                print ex
        if musicGenresResource.issharing:
            try:
                musicGenres =answerListCollection.find({ "key": "MusicGenres" })
                musicGenres = musicGenres[0]["value"] if musicGenres.count() > 0 else []
                template["musicGenres"] = musicGenres
            except Exception:
                print "RDF Failed"
        if friendsResource.issharing:
            try:
                friends = answerListCollection.find({ "key": "Friends" })
                friends = friends[0]["value"] if friends.count() > 0 else []
                template["friends"] = friends
            except Exception:
                print "RDF Failed when fetching friends"
    return render_to_response(
        "personalProfile.rdf", 
        template, 
        RequestContext(request),
        mimetype="application/rdf+xml")

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

def funfSetting(request):
    data = {}
    outputMessage = ''
    if request.method=="POST":
        submittedForm = FunfProbeSettingForm(request.POST)
        if submittedForm.is_valid():
	    cleanedData = submittedForm.cleaned_data
	    data = {'activityProbe' : cleanedData['activityProbe'],
            	'smsProbe' : cleanedData['smsProbe'],
            	'callLogProbe' : cleanedData['callLogProbe'],
            	'bluetoothProbe' : cleanedData['bluetoothProbe'],
            	'wifiProbe' : cleanedData['wifiProbe'],
           	'simpleLocationProbe' : cleanedData['simpleLocationProbe'],
            	'screenProbe' : cleanedData['screenProbe'],
            	'runningApplicationsProbe' : cleanedData['runningApplicationsProbe'],}
    	    outputMessage = 'The setting has been updated!'
	    submittedForm.save()
    else:
    	funfProbe = FunfProbeModel.objects.get(funfPK='funfPK')
    	data = {'activityProbe' : funfProbe.activityProbe,
	    'smsProbe' : funfProbe.smsProbe,
	    'callLogProbe' : funfProbe.callLogProbe,
	    'bluetoothProbe' : funfProbe.bluetoothProbe,
	    'wifiProbe' : funfProbe.wifiProbe,
	    'simpleLocationProbe' : funfProbe.simpleLocationProbe,
	    'screenProbe' : funfProbe.screenProbe,
	    'runningApplicationsProbe' : funfProbe.runningApplicationsProbe}
    	outputMessage = 'Select probes to grant access.'

    form = FunfProbeSettingForm(initial=data, label_suffix="")

    return render_to_response('funfSetting.html', {'form':form, 'output_message':outputMessage })
