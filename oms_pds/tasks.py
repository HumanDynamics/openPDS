from celery import task
from oms_pds.pds.models import Profile
from bson import ObjectId
from pymongo import Connection
from django.conf import settings
import time
from datetime import date 
import json
import pdb

from oms_pds.pds.models import Profile

"""the MONGODB_DATABASE_MULTIPDS setting is set by extract-user-middleware in cases where we need multiple PDS instances within one PDS service """


connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)


@task()
def add(x, y):
    print "Test"
    return x + y

@task()
def activityForLastHour():
    profiles = Profile.objects.all()
    
    print "Entered aggregation"
    
    aggregates = {}
    
    for profile in profiles:
        # Get the mongo store for the given user
        dbName = "User_" + str(profile.id)
        collection = connection[dbName]["funf"]
        
        # funf timestamps are represented as millis since epoch
        
        currentTime = time.mktime(time.gmtime())
        oneHourAgo = currentTime - (3600 * 24 * 30)
        
        #currentTime *= 1000
        #oneHourAgo *= 1000
        
        lowActivityIntervals = highActivityIntervals = totalIntervals = 0
        
        print dbName
        print profile.id, profile.uuid
        
        for data in collection.find({ "key": { "$regex" : "ActivityProbe$" }, "time": { "$gte" : oneHourAgo }}):
            dataValue = json.loads(data.value)
            print dataValue
            totalIntervals += dataValue["total_intervals"]
            lowActivityIntervals += dataValue["low_activity_intervals"]
            highActivityIntervals += dataValue["high_activity_intervals"]
        
        aggregates[profile.uuid] = { "total": totalIntervals, "low": lowActivityIntervals, "high": highActivityIntervals }
    
    return aggregates

def activityForTimeRange(collection, start, end):
    lowActivityIntervals = highActivityIntervals = totalIntervals = 0
    
    for data in collection.find({ "key": { "$regex" : "ActivityProbe$" }, "time": { "$gte" : start, "$lt":end }}):
        #pdb.set_trace()
        dataValue = data["value"]
        totalIntervals += dataValue["total_intervals"]
        lowActivityIntervals += dataValue["low_activity_intervals"]
        highActivityIntervals += dataValue["high_activity_intervals"]
    
    return { "total": totalIntervals, "low": lowActivityIntervals, "high": highActivityIntervals }

@task()
def activityForToday():
    profiles = Profile.objects.all()
    aggregates = {}
    
    # Note: left off setting midnight to loop over hours until now... 
    currentTime = time.mktime(time.gmtime())
    # Interesting way of getting midnight for the day of the current GM time.... is there a better way?
    midnight = time.mktime(date.fromtimestamp(currentTime - (3600 * 24 * 2)).timetuple())

    for profile in profiles:
        # Get the mongo store for the given user
        dbName = "User_" + str(profile.id)
        collection = connection[dbName]["funf"]
        aggregates[profile.uuid] = {}
        
        for offsetFromMidnight in range(int(midnight), int(currentTime), 3600):
            hour = (offsetFromMidnight - midnight) / 3600
            
            aggregates[profile.uuid][hour] = activityForTimeRange(collection, offsetFromMidnight, offsetFromMidnight + 3600)
        
        answer = { "key": "activityByHour" }
        answer["value"] = aggregates[profile.uuid]
        
        connection[dbName]["answerlist"].insert(answer)
    
    return aggregates