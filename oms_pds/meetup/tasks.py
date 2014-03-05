from celery import task
from oms_pds.pds.models import Profile, Notification, Device
from bson import ObjectId
from pymongo import Connection
from django.conf import settings
import time
from datetime import date, timedelta
import json
import pdb
import math
import cluster
import requests
from gcm import GCM
from oms_pds.pds.models import Profile
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
from oms_pds.meetup.internal import getInternalDataStore
from oms_pds.places_tasks import centroid, distanceBetweenLatLongs
import sqlite3

def scoreMeetup(places):
    if len(places) == 0:
        return 99999999
    center = centroid([(p["bounds"][0], p["bounds"][1]) for p in places])
    distances = [distanceBetweenLatLongs(center, (p["bounds"][0], p["bounds"][1])) for p in places]
    distance_score = reduce(lambda d1, d2: d1 +  d2, distances, 0)
    average_distance = distance_score / len(places)
    variance_score = math.sqrt(reduce(lambda s, d: s + (d - average_distance)**2, distances, 0))
    return distance_score + variance_score, center

def updateMeetupScore(total_distance, total_variance, center, numUsers, place):
    place_point = (place["bounds"][0], place["bounds"][1])
    center_sum = (center[0] * numUsers, center[1] * numUsers)
    print "%s %s %s"%(place["key"],center, place_point)
    new_center = ((center_sum[0] + place_point[0]) / (numUsers + 1), (center_sum[1] + place_point[1]) / (numUsers + 1))
    distance = distanceBetweenLatLongs(new_center, place_point)
    new_distance = total_distance + distance
    average_distance = new_distance / (numUsers + 1)
    new_variance = math.sqrt(total_variance**2 + (distance - average_distance)**2)

    return new_distance, new_variance, new_center

@task()
def initiateMeetupScheduling(owner_uuid, meetup_uuid, token):
    owner = Profile.objects.get(uuid = owner_uuid)
    internalDataStore = getInternalDataStore(owner, token)
    meetup_request = internalDataStore.getMeetupRequest(meetup_uuid)

    owner_places = internalDataStore.getAnswerList("RecentPlaces")[0]["value"]

    answer = []
    
    for place in [p for p in owner_places if p["key"] not in ["work", "home"]]:
        answer.append({"key": place["key"], "total_distance": 0, "total_variance": 0, "center": (0,0) })

    #internalDataStore.saveAnswer("Meetup%s"%meetup_uuid, answer)

    next_uuid = meetup_request["participants"][0]
    
    print "%s initiating meetup scheduling for %s"%(owner_uuid, meetup_uuid)
    next_contribution_url = "http://working-title.media.mit.edu:8004/meetup/help_schedule?meetup_uuid=%s&bearer_token=%s&datastore_owner__uuid=%s"%(meetup_uuid, token, next_uuid)
    requests.post(next_contribution_url, data=json.dumps(answer), headers={"content-type":"application/json"})

@task()
def helpScheduleMeetup(owner_uuid, meetup_uuid, running_totals, token):
    print "%s contributing to meetup %s"%(owner_uuid, meetup_uuid)
    owner = Profile.objects.get(uuid = owner_uuid)
    internalDataStore = getInternalDataStore(owner, token)
    meetup_request = internalDataStore.getMeetupRequest(meetup_uuid)
    requester_uuid = meetup_request["requester"]

    participant_uuids = meetup_request["participants"]
    my_index = len(participant_uuids) if owner_uuid == requester_uuid else participant_uuids.index(owner_uuid)
    #previous_uuid = participant_uuids[my_index - 1] if my_index > 0 else requester_uuid
    #running_totals_url = "http://working-title.media.mit.edu:8004/api/personal_data/answerlist/?key=Meetup%s&datastore_owner__uuid=%s&bearer_token=%s"%(meetup_uuid, previous_uuid, token)
    #r = requests.get(running_totals_url, headers = {"content-type": "application/json"})
    #if r.status_code != requests.codes.ok:
    #    return
    #running_totals = r.json()[0]["value"]
  
    owner_places = internalDataStore.getAnswerList("RecentPlaces")[0]["value"]
    answer = []
    for scores in running_totals:
        key = scores["key"]
        place = next((p for p in owner_places if p["key"] == key), None)
        total_distance = scores["total_distance"]
        total_variance = scores["total_variance"]
        center = scores["center"]
        if place is not None:
            new_distance, new_variance, new_center = updateMeetupScore(total_distance, total_variance, center, my_index, place)
        else:
            new_distance = total_distance + 99999999
            new_variance = total_variance + 99999999
            new_center = center
        answer.append({"key": key, "total_distance": new_distance, "total_variance": new_variance, "center": new_center})

    internalDataStore.saveAnswer("Meetup%s"%meetup_uuid, answer)
    if my_index < len(participant_uuids) - 1: 
        next_uuid = participant_uuids[my_index + 1]
    else:
        next_uuid = requester_uuid
    
    if owner_uuid == requester_uuid:
        chooseMeetupAndPushResult(meetup_request, answer)
    else:
        next_contribution_url = "http://working-title.media.mit.edu:8004/meetup/help_schedule?meetup_uuid=%s&bearer_token=%s&datastore_owner__uuid=%s"%(meetup_uuid, token, next_uuid)
        requests.post(next_contribution_url,data=json.dumps(answer),headers={"content-type":"application/json"})

def chooseMeetupAndPushResult(meetup_request, running_totals):
    print "Choosing meetup %s" % meetup_request
    running_totals.sort(key = lambda scores: -(scores["total_distance"] + math.sqrt(scores["total_variance"])))
    top = running_totals[0]
    print top
    

@task()
def scheduleMeetup(owner_uuid="280e418a-8032-4de3-b62a-ad173fea4811", meetup_uuid="", token="b3dbac8916"):
     
    participant_uuids=["5241576e-43da-4b08-8a71-b477f931e021", "72d9d8e3-3a57-4508-9515-2b881afc0d8e"]
    participant_places = {}
    owner = Profile.objects.get(uuid = owner_uuid)
    internalDataStore = getInternalDataStore(owner, token)
    meetup_request = internalDataStore.getMeetupRequest(meetup_uuid)
    if meetup_request is None or "approved" not in meetup_request or not meetup_request["approved"]:
        return 
    owner_places = internalDataStore.getAnswerList("RecentPlaces")[0]["value"]

    for uuid in participant_uuids:
        url = "http://working-title.media.mit.edu:8004/api/personal_data/answerlist/?key=RecentPlaces&datastore_owner__uuid=%s&bearer_token=%s"%(uuid, token)
        headers = { "content-type": "application/json" }
        requester_places = requests.get(url, headers = headers)
        print "Meetup between %s and %s"%(owner_uuid, uuid)
        if requester_places.status_code == requests.codes.ok:
            print requester_places.json()
            participant_places[uuid] = requester_places.json()["objects"][0]["value"]

    min_score = 9999999999 #proxy for int_max or whatever Python calls it
    min_score_key = None
    meeting_point = None
    participant_locations = []
    for place in [p for p in owner_places if p["key"] not in ["work", "home"]]:
        #print participant_places
        places_for_key = [p for uid in participant_uuids for p in participant_places[uid] if p["key"] == place["key"]]
        places_for_key.append(place)        
        score_for_key, point_for_key = scoreMeetup(places_for_key)  
        if score_for_key < min_score:
            print "%s < %s" % (score_for_key, min_score)
            min_score = score_for_key
            min_score_key = place["key"]
            meeting_point = point_for_key
            participant_locations = [(p["bounds"][0], p["bounds"][1]) for p in places_for_key]

    print "Best Time: %s" % min_score_key
    print "Meeting point: %s,%s" % meeting_point
    print participant_locations
    answer = internalDataStore.getAnswerList("Meetups")
    answer = answer[0]["value"] if answer is not None and answer.count() > 0 else []
    answer = [v for v in answer if "description" in v and v["description"] != description]
    answer.append({"description": description, "participants": participant_uuids, "hour": min_score_key, "place": meeting_point})
    internalDataStore.saveAnswer("Meetups", answer)
