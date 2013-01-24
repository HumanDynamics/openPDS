from celery import task
from oms_pds.pds.models import Profile
from bson import ObjectId
from pymongo import Connection
from django.conf import settings
import time
from datetime import date, timedelta
import json
import pdb
import math

from oms_pds.pds.models import Profile

"""the MONGODB_DATABASE_MULTIPDS setting is set by extract-user-middleware in cases where we need multiple PDS instances within one PDS service """


connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

def activityForTimeRange(collection, start, end):
    lowActivityIntervals = highActivityIntervals = totalIntervals = 0
    
    for data in collection.find({ "key": { "$regex" : "ActivityProbe$" }, "time": { "$gte" : start, "$lt":end }}):
        #pdb.set_trace()
        dataValue = data["value"]
        totalIntervals += dataValue["total_intervals"]
        lowActivityIntervals += dataValue["low_activity_intervals"]
        highActivityIntervals += dataValue["high_activity_intervals"]
    
    return { "start": start, "end": end, "total": totalIntervals, "low": lowActivityIntervals, "high": highActivityIntervals }

def aggregateActivityForAllUsers(answerKey, startTime, endTime):
    profiles = Profile.objects.all()
    aggregates = {}
    
    for profile in profiles:
        # Get the mongo store for the given user
        dbName = "User_" + str(profile.id)
        collection = connection[dbName]["funf"]
        aggregates[profile.uuid] = []
        
        for offsetFromStart in range(int(startTime), int(endTime), 3600):
            aggregates[profile.uuid].append(activityForTimeRange(collection, offsetFromStart, offsetFromStart + 3600))
        
        answer = connection[dbName]["answerlist"].find({ "key": answerKey })
        
        if answer.count() == 0:
            answer = { "key": answerKey }
        else:
            answer = answer[0]
 
        answer["data"] = aggregates[profile.uuid]
        
        connection[dbName]["answerlist"].save(answer)
    
    return aggregates

@task()
def recentActivity():
    currentTime = time.mktime(time.gmtime())
    today = date.fromtimestamp(currentTime)
    answerKey = "RecentActivityByHour"
    startTime = time.mktime((today - timedelta(days=7)).timetuple())
        
    return aggregateActivityForAllUsers(answerKey, startTime, currentTime)

@task()
def activityForThisMonth():
    currentTime = time.mktime(time.gmtime())
    today = date.fromtimestamp(currentTime)
    answerKey = "ActivityByHour" + today.strftime("%Y%m")
    startTime = time.mktime(today.replace(day = 1).timetuple())

    return aggregateActivityForAllUsers(answerKey, startTime, currentTime)

def totalActivityForHour(activityForHour):
    return activityForHour.low + activityForHour.high

@task 
def recentActivityScore():
    data = recentActivity()
    score = {}
    
    for uuid, activityList in data:
        recentTotals = map(totalActivityForHour, activityList)
        score[uuid] = min(1.75*math.log(2 + sum(recentTotals) / 50.0) - 1, 10)
    
    return score[uuid]