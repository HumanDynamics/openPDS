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
from gcm import GCM
from oms_pds.pds.models import Profile
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter

"""the MONGODB_DATABASE_MULTIPDS setting is set by extract-user-middleware in cases where we need multiple PDS instances within one PDS service """


connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

def getDBName(profile):
    return "User_" + str(profile.uuid).replace("-", "_")

def getTopAccessPointsForTimeRange(collection, start, end):
    accessPoints = collection.find({ "key": { "$regex" : "WifiProbe$" }, "time": { "$gte" : start, "$lt":end }})
    if accessPoints.count() > 0:
        accessPoints = [ap["value"] for ap in accessPoints]
        if len(accessPoints) < 5:
            return [ap["bssid"] for ap in accessPoints]
        sortedAccessPoints = sorted(accessPoints, key=lambda value: -value["level"])
        return [ap["bssid"] for ap in sortedAccessPoints[0:5]]

def getTopAccessPointsForUser(profile):
    funf = connection[getDBName(profile)]["funf"]
    currentTime = time.time()
    today = date.fromtimestamp(currentTime)
    firstTime = time.mktime((today - timedelta(days=3)).timetuple())
    startTimes = [start for start in range(int(firstTime), int(currentTime) - 3600*4, 600)]

    allTopAccessPoints = []

    for startTime in startTimes:
        topAccessPoints = getTopAccessPointsForTimeRange(funf, startTime, startTime + 600)
        if topAccessPoints is not None:
            allTopAccessPoints.extend(topAccessPoints)
    return set(sorted(allTopAccessPoints))

def getTopAccessPoints():
    profiles = Profile.objects.all()
    accessPoints = {}
    intersections = {}
    notUnique = {}
    for profile in profiles:
        accessPoints[profile.uuid] = getTopAccessPointsForUser(profile)
   
    for profile in profiles:
        if len(accessPoints[profile.uuid]) > 0:
            unique = True
            intersections[profile.uuid] = {} 
            notUnique[profile.uuid] = []
            maxIntersection = 0
            #print profile.uuid
            for profile2 in profiles:
                intersections[profile.uuid][profile2.uuid] = accessPoints[profile.uuid].intersection(accessPoints[profile2.uuid])
                notUnique[profile.uuid].extend(intersections[profile.uuid][profile2.uuid])
                if profile.uuid <> profile2.uuid:
                    if len(intersections[profile.uuid][profile2.uuid]) > maxIntersection:
                        maxIntersection = len(intersections[profile.uuid][profile2.uuid])
                    if len(intersections[profile.uuid][profile2.uuid]) >= len(accessPoints[profile.uuid]):
                        unique = False
            notUnique[profile.uuid] = set(notUnique[profile.uuid])
            answerCollection = connection[getDBName(profile)]["answer"]
            answerCollection.remove({ "key": "Uniqueness" })
            answer = { "key": "Uniqueness" }
            answer["value"] = { "message": "Your data uniquely identifies you" if unique else "Your data is not unique" }
            answer["value"]["wifi_count"] = len(accessPoints[profile.uuid])
            answer["value"]["unique_wifi_count"] = len(accessPoints[profile.uuid]) - maxIntersection
            answerCollection.save(answer)
    
            #print accessPoints[profile.uuid]
            print str(len(accessPoints[profile.uuid])) + "," + str(maxIntersection)
            #print intersections[profile.uuid]
            #print answer
            #print "\n"

