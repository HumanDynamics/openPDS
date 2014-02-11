from celery import task
from oms_pds.pds.models import Profile, Notification, Device
from bson import ObjectId
from pymongo import Connection
from django.conf import settings
import time
from datetime import date, timedelta, datetime
import json
import pdb
import math
import cluster
from gcm import GCM

from oms_pds.pds.models import Profile

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)


@task()
def findRecentIncidents():
    currentTime = time.time()
    today = date.fromtimestamp(currentTime)
    startTime = currentTime - (3600 * 24)#time.mktime((today - timedelta(days=1)).timetuple())

    profiles = Profile.objects.all()
    answer = { "key": "RecentIncidents", "value": [] }
    print "Aggregating incidents over the last day..."
    for profile in profiles:
        dbName = profile.getDBName()
        collection = connection[dbName]["incident"]
        for incident in collection.find({ "date": { "$gte": startTime } }, limit=50):
            answer["value"].append(incident)

    print "Storing %i incidents into %i profiles..." % (len(answer["value"]), profiles.count())
    for profile in profiles:
        dbName = profile.getDBName()
        answerlistCollection = connection[dbName]["answerlist"]
        answerlistCollection.remove({ "key": "RecentIncidents" })
        answerlistCollection.save(answer)
    print "Done."

@task()
def ensureIncidentIndexes():
    profiles = Profile.objects.all()

    for profile in profiles:
        dbName = profile.getDBName()
        collection = connection[dbName]["incident"]
        collection.ensure_index([("date", -1), ("type", 1)], cache_for=7200, background=True)

