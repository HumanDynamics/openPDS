from celery import task
from oms_pds.pds.models import Profile, Notification
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
    score = 0
    
    # For now, we're just taking the most recent probe value and checking message / call dates within it
    # This will not account for messages or call log entries that might have been deleted.
    
    # NOTE: we're including the start date in the queries below to simply shrink the number of entries we need to sort
    # Given that SMS and call log probes may include all messages and calls stored on the phone, we can't just look
    # at entries collected during that time frame
    
#    smsEntries = collection.find({ "key": { "$regex": "SMSProbe$" }, "time": {"$gte": start}})
#    
#    if smsEntries.count() > 0:
#        # Message times are recorded at the millisecond level. It should be safe to use that as a unique id for messages
#        messageSets = [smsEntry["value"]["messages"] for smsEntry in smsEntries]
#        messages = set([message for messageSet in messageSets for message in messageSet if message["date"] >= start*1000 and message["date"] < end*1000])
#        
#        # We're assuming a hit on a thread is equivalent to a single phone call
#        messageCountByThread = {}
#        
#        for threadId in [message["thread_id"] for message in messages]:
#            messageCountByAddress[threadId] = len([message for message in messages if message["threadId"] if message["thread_id"] = ])
#        #messageTimes = set([message["date"] for message in messages if message["date"] >= start*1000 and message["date"] < end*1000])
#        smsCount = len(messageTimes)
    
    callLogEntries = collection.find({ "key": { "$regex": "CallLogProbe$" }, "time": {"$gte": start}})
    
    if callLogEntries.count() > 0:
        callSets = [callEntry["value"]["calls"] for callEntry in callLogEntries]
        calls = [call for callSet in callSets for call in callSet if call["date"] >= start*1000 and call["date"] < end*1000]
        
        #callTimes = set([call["date"] for call in calls if call["date"] >= start*1000 and call["date"] < end*1000])
        countsByNumber = [float(len([call for call in calls if call["number"] == numberHash])) for numberHash in [call["number"] for call in calls]]
        totalCalls = sum(countsByNumber)
        frequencies = [count / totalCalls for count in countsByNumber]
        score =sum([-frequency * math.log(frequency, 10) for frequency in frequencies]) * 10
    
    return { "start": start, "end": end, "social": score}

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
def recentActivityLevels():
    currentTime = time.time()
    today = date.fromtimestamp(currentTime)
    answerKey = "RecentActivityByHour"
    startTime = time.mktime((today - timedelta(days=6)).timetuple())
        
    return aggregateForAllUsers(answerKey, startTime, currentTime, activityForTimeRange)

@task()
def recentFocusLevels():
    currentTime = time.time()
    answerKey = "RecentFocusByHour"
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=6)).timetuple())
    
    return aggregateForAllUsers(answerKey, startTime, currentTime, focusForTimeRange)

@task()
def recentSocialLevels():
    currentTime = time.time()
    answerKey = "RecentSocialByHour"
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=6)).timetuple())
    
    return aggregateForAllUsers(answerKey, startTime, currentTime, socialForTimeRange)

@task() 
def recentActivityScore():
    data = recentActivityLevels()
    score = {}
    
    for uuid, activityList in data.iteritems():
        recentTotals = [item["low"] + item["high"] for item in activityList]
        score[uuid] = min(1.75*math.log(2 + sum(recentTotals) / 50.0, 2) - 1, 10)
    
    return score

@task()
def recentFocusScore():
    data = recentFocusLevels()
    score = {}

    for uuid, focusList in data.iteritems():
        recentTotals = [item["focus"] for item in focusList]
        score[uuid] = min(math.log(1 + sum(recentTotals), 2), 10)

    return score

@task()
def recentSocialScore():
    data = recentSocialLevels()
    score = {}
    
    for uuid, socialList in data.iteritems():
        recentTotals = [item["social"] for item in socialList]
        score[uuid] = float(sum(recentTotals)) / len(recentTotals)
        
    return score

def addNotification(profile, notificationType, title, content):    
    notification, created = Notification.objects.get_or_create(datastore_owner=profile, type=notificationType)
    notification.title = title
    notification.content = content
    notification.datastore_owner = profile
    notification.save()    

@task() 
def checkDataAndNotify():
    profiles = Profile.objects.all()
    data = {}
    
    currentTime = time.time()
    recentTime = currentTime - 3600 * 2
    
    for profile in profiles:
        dbName = "User_" + str(profile.id)
        collection = connection[dbName]["funf"]
       
        recentEntries = collection.find({ "time": {"$gte": recentTime }})
        
        if (recentEntries.count() == 0):
            addNotification(profile, 1, "Stale behavioral data", "Analysis may not accurately reflect your behavior.")

@task()
def recentSocialHealthScores():
    profiles = Profile.objects.all()
    data = {}
    
    activityScores = recentActivityScore()
    socialScores = recentSocialScore()
    focusScores = recentFocusScore()
    
    for profile in profiles:
        dbName = "User_" + str(profile.id)
        collection = connection[dbName]["answerlist"]
        
        answer = collection.find({ "key" : "socialhealth" })
        answer = answer[0] if answer.count() > 0 else {"key": "socialhealth", "data":[]} 
        
        data[profile.uuid] = [datum for datum in answer["data"] if datum["layer"] != "User"]
        data[profile.uuid].append({ "key": "activity", "layer": "User", "value": activityScores[profile.uuid] })
        data[profile.uuid].append({ "key": "social", "layer": "User", "value": socialScores[profile.uuid] })
        data[profile.uuid].append({ "key": "focus", "layer": "User", "value": focusScores[profile.uuid] })
        
        answer["data"] = data[profile.uuid]
        
        collection.save(answer)
    return data
   
