import uuid
import json
import pdb
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.core.exceptions import ObjectDoesNotExist
from oms_pds.pds.models import Profile
from oms_pds.meetup.internal import getInternalDataStore
from oms_pds.meetup.tasks import scheduleMeetup, helpScheduleMeetup, initiateMeetupScheduling
from oms_pds import settings

def get_parameters(request, params):
    values = []
    for param in params:
        if param not in request.GET:
            return []
        values.append(request.GET[param])
    return values

def meetup_home(request):
    params = get_parameters(request, ["bearer_token", "datastore_owner"]);
    profile_api_url = "http://%s/account/api/v1/profile/"%settings.SERVER_OMS_REGISTRY
    template = { "PROFILE_API_URL": profile_api_url, "STATIC_URL": settings.STATIC_URL}
    return render_to_response("meetup/meetup_home.html", template)

def create_request(request):
    params = get_parameters(request, ["bearer_token", "datastore_owner"])
    profile_api_url = "http://%s/account/api/v1/profile/"%settings.SERVER_OMS_REGISTRY
    template = { "PROFILE_API_URL": profile_api_url, "STATIC_URL": settings.STATIC_URL}
    return render_to_response("meetup/create_meetup_request.html", template)

def request_meetup(request):
    params = get_parameters(request, ["bearer_token", "datastore_owner__uuid"])
    participants = ["280e418a-8032-4de3-b62a-ad173fea4811", "72d9d8e3-3a57-4508-9515-2b881afc0d8e"]
    meetup_request = {"description": "Test meetup", "uuid": "%s"%uuid.uuid4(), "requester": params[1], "participants": participants}

    profile = Profile.objects.get(uuid = params[1])
    ids = getInternalDataStore(profile, params[0])
    ids.addMeetupRequest(meetup_request["uuid"], meetup_request["requester"], meetup_request["participants"], meetup_request["description"])
    url = "http://working-title.media.mit.edu:8004/api/personal_data/meetup_request/?datastore_owner__uuid=%s&bearer_token=%s"
    print "%s"%meetup_request
    payload = json.dumps(meetup_request)
    headers = {"content-type": "application/json"}

    for participant in participants:
        r = requests.post(url%(participant, params[0]), data=payload, headers=headers)
        if r.status_code != requests.codes.ok:
            print "Failed sending meetup request %s to %s"%(meetup_request["uuid"],participant)
    
    return HttpResponse('{"success": true}', content_type="application/json")

def update_approval_status(request):
    params = get_parameters(request, ["meetup_uuid", "participant", "bearer_token", "datastore_owner", "approved"])
    if len(params) == 0:
        return HttpResponse("", status = 401)
    
    token = params[2]
    owner_uuid = params[3]
    meetup_uuid = params[0]
    participant_uuid = params[1]
    approved = params[4]

    profile = Profile.objects.get(uuid = owner_uuid)

    ids = getInternalDataStore(profile, token)
    if approved:
        ids.addParticipantToApprovals(meetup_uuid, participant_uuid)
    # NOTE: what to do if approved is False? Remove them from approvals or from the participants also? What if the computation has already started?
    #else:
    #    ids.removeParticipantFromMeetupRequest(meetup_uuid, participant_uuid)
    meetup_request = ids.getMeetupRequest(meetup_uuid)
    if "approvals" in meetup_request and len(meetup_request["approvals"]) == len(meetup_request["participants"]):
        initiateMeetupScheduling.apply_async(args=(owner_uuid, meetup_uuid, token))
    #scheduleMeetup.apply_async(args=(owner_uuid, meetup_uuid, token))
    return HttpResponse("")

def contribute_to_scheduling(request):
    params = get_parameters(request, ["meetup_uuid", "bearer_token", "datastore_owner__uuid"])

    if len(params) == 0:
        return HttpResponse("", status=401)

    if request.method != "POST": 
        return HttpResponse('{"message": "This endpoint is only configured for POSTs", "success": false}', content_type="application/json")

    running_totals = json.loads(request.body)
    helpScheduleMeetup.apply_async(args=(params[2], params[0], running_totals, params[1]))
    return HttpResponse("")
