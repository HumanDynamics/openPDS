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

def focusForTimeRange(collection, start, end):
    screenOnCount = 0
    
    for data in collection.find({ "key": { "$regex": "ScreenProbe$" }, "time": {"$gte": start, "$lt": end }}):
        dataValue = data["value"]
        screenOnCount += 1 if dataValue["screen_on"] else 0
    
    return { "start": start, "end": end, "focus": screenOnCount }

def socialForTimeRange(collection, start, end):
    smsCount = callCount = 0
    
    # For now, we're just taking the most recent probe value and checking message / call dates within it
    # This will not account for messages or call log entries that might have been deleted.
    
    # NOTE: we're including the start date in the queries below to simply shrink the number of entries we need to sort
    # Given that SMS and call log probes include all messages and calls stored on the phone, only the most recent is 
    # completely necessary.
    
    smsEntries = collection.find({ "key": { "$regex": "SMSProbe$" }, "time": {"$gte": start}}).sort("time", -1)
    
    if smsEntries.count() > 0:
        dataValue = smsEntries[0]["value"]
        messages = [message for message in dataValue["messages"] if message["date"] >= start*1000 and message["date"] < end*1000]
        smsCount = len(messages)
    
    callEntries = collection.find({ "key": { "$regex": "CallLogProbe$" }, "time": {"$gte": start}}).sort("time", -1)
    
    if callEntries.count() > 0:
        dataValue = callEntries[0]["value"]
        calls = [call for call in dataValue["calls"] if call["date"] >= start*1000 and call["date"] < end*1000]
        callCount = len(calls)

    return { "start": start, "end": end, "social": smsCount + callCount}

def aggregateForAllUsers(answerKey, startTime, endTime, aggregator):
    profiles = Profile.objects.all()
    aggregates = {}
    
    for profile in profiles:
        dbName = "User_" + str(profile.id)
        collection = connection[dbName]["funf"]
        aggregates[profile.uuid] = []
        
        for offsetFromStart in range(int(startTime), int(endTime), 3600):
            aggregates[profile.uuid].append(aggregator(collection, offsetFromStart, offsetFromStart + 3600))
        
        answer = connection[dbName]["answerlist"].find({ "key" : answerKey })
        
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
        
    return aggregateForAllUsers(answerKey, startTime, currentTime, activityForTimeRange)

@task()
def recentFocus():
    currentTime = time.mktime(time.gmtime())
    answerKey = "RecentFocusByHour"
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=7)).timetuple())
    
    return aggregateForAllUsers(answerKey, startTime, currentTime, focusForTimeRange)

@task()
def recentSocial():
    currentTime = time.mktime(time.gmtime())
    answerKey = "RecentSocialByHour"
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=7)).timetuple())
    
    return aggregateForAllUsers(answerKey, startTime, currentTime, socialForTimeRange)

@task()
def activityForThisMonth():
    currentTime = time.mktime(time.gmtime())
    today = date.fromtimestamp(currentTime)
    answerKey = "ActivityByHour" + today.strftime("%Y%m")
    startTime = time.mktime(today.replace(day = 1).timetuple())

    return aggregateForAllUsers(answerKey, startTime, currentTime, activityForTimeRange)

def totalActivityForHour(activityForHour):
    return activityForHour["low"] + activityForHour["high"]

@task 
def recentActivityScore():
    data = recentActivity()
    score = {}
    #pdb.set_trace() 
    for uuid, activityList in data.iteritems():
        recentTotals = map(totalActivityForHour, activityList)
        score[uuid] = min(1.75*math.log(2 + sum(recentTotals) / 50.0) - 1, 10)
    
    return score

@task 
def recentFocusScore():
    data = recentFocus()
    score = {}

    for uuid, activityList in data.iteritems():
        recentTotals = [item["focus"] for item in activityList]
        score[uuid] = min(math.log(1 + sum(recentTotals)), 10)

    return score
