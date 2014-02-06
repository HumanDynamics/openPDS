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
#from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
import sqlite3

"""the MONGODB_DATABASE_MULTIPDS setting is set by extract-user-middleware in cases where we need multiple PDS instances within one PDS service """


connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

def getDBName(profile):
    return "User_" + str(profile.id) #str(profile.uuid).replace("-", "_")

def LNPDF(x, loc, scale):
    return math.exp(-(math.log(x)-loc)**2/(2*(scale**2))) / (x*math.sqrt(2*math.pi)*scale)

def CDF(x, mean, dev):
    return 0.5 * (1 + math.erf((x - mean) / (dev * math.sqrt(2))))

#def focusForHours(screenOns, hours=4):
#    #Note: threw this together so zero screen-ons = zero score (potentially sleeping?), peek focus of 10 at 12 screen-ons over 4 hours
#    
#    factor = 4.0 / hours
#    x = float(screenOns) * factor
#    #x = 0.05 * x + 0.6 
#    #print 2.27*x*((1.087)**-x)
#    #return 2.27*x*((1.087)**-x)
#    return 10 if (x < 4) else 10.0 * math.exp(-0.25*x + 1)
#    #return 11.0 * LNPDF(x, 0, 0.5)

def computeActivityScore(activityList):
    recentActiveTotals = [1.0 * float(item["low"]) + item["high"] for item in activityList]
    recentTotal = float(sum([item["total"] for item in activityList]))
     
    factor = 1000.0 / recentTotal if recentTotal > 0 else 1
    activeTotal = factor * float(sum(recentActiveTotals))
    #factor = baselineTotal / recentTotal if recentTotal > 0 else 1
#    return min(1 / (1 + math.exp(center - sum(recentActiveTotals))), 10)
#    return  min(2.538 * (math.log(2 + factor * float(sum(recentActiveTotals)) / 8.89, 2) - 1), 10)
#    return min(5 * (1 + math.erf((activeTotal - 44.5) / 44.5)), 10)
    #NOTE: mean=54, stdDev=13. Dev changed to make graphs nicer
    #print 10 * CDF(41, 54, 39)
    #print 10 * CDF(67, 54, 39)
    return min(10.0 * CDF(activeTotal, 54, 39), 10)

def computeFocusScore(focusList):
    recentTotals = [item["focus"] for item in focusList]
    x = float(sum(recentTotals))
    
#    return min(math.log(1 + sum(recentTotals), 2), 10) 
    # NOTE: mean=98, stdDev = 26. Dev changed to make graphs nicer
    # Updated focus score: 184.5, 21.7
#    print 10 * CDF(72, 98,52)
#    print 10 * CDF(124, 98, 52)
    return min(10.0 * CDF(float(sum(recentTotals)), 184.5, 88), 10)

def computeSocialScore(socialList):
    recentTotals = [item["social"] for item in socialList]
    # 68.8, 33.8
    return min(10.0 * CDF(float(sum(recentTotals)), 68.8, 68.8), 10)


def intervalsOverlap(i1, i2):
    return i2[0] <= i1[0] <= i2[1] or i2[0] <= i1[1] <= i2[1] or i1[0] <= i2[0] <= i1[1] or i1[0] <= i2[1] <= i1[1]


def selfAssessedScoreForTimeRange(collection, start, end, metric):
    verificationEntries = collection.find({ "key": metric + "Verification"})
    past3DaysEntries = collection.find({ "key": metric + "Past3Days" })
    oneDay = 24 * 3600

    v = []

    if verificationEntries.count() > 0:
        for answerList in verificationEntries:
            v.extend([value for value in answerList["value"]])

    p = []
    if past3DaysEntries.count() > 0:
        for answerList in past3DaysEntries:
            p.extend([value for value in answerList["value"]])

    v = [value for value in v if intervalsOverlap([value["time"] - oneDay, value["time"]], [start, end])]
    p = [value for value in p if intervalsOverlap([value["time"] - 3*oneDay, value["time"]], [start, end])]
    #pdb.set_trace()
    v.extend(p)

    allScores = [int(value["value"]) for value in v]

    average = sum(allScores) / len(allScores) if len(allScores) > 0 else 0

    return {"start": start, "end": end, "value": average * 2.0 }


def activityForTimeRange(collection, start, end, includeBlanks = False, answerlistCollection=None):
    lowActivityIntervals = highActivityIntervals = totalIntervals = 0

    activityEntries = collection.find({ "key": { "$regex" : "ActivityProbe$" }, "time": { "$gte" : start, "$lt":end }})
    if includeBlanks or activityEntries.count() > 0:
        for data in activityEntries:
            #pdb.set_trace()
            dataValue = data["value"]
            if ("total_intervals" in dataValue):
                totalIntervals += dataValue["total_intervals"]
                lowActivityIntervals += dataValue["low_activity_intervals"]
                highActivityIntervals += dataValue["high_activity_intervals"]
            else:
                totalIntervals += 1
                lowActivityIntervals += 1 if dataValue["activitylevel"] == "low" else 0
                highActivityIntervals += 1 if dataValue["activitylevel"] == "high" else 0

        activity = { "start": start, "end": end, "total": totalIntervals, "low": lowActivityIntervals, "high": highActivityIntervals }
        if answerlistCollection is not None:
            selfAssessed = selfAssessedScoreForTimeRange(answerlistCollection, start, end, "Activity")
            activity["selfAssessed"] = selfAssessed["value"]
        return activity
    return None

def focusForTimeRange(collection, start, end, includeBlanks = False, answerlistCollection=None):
    screenOnCount = 0
    hours = float((end - start)) / 3600.0

    screenOnEntries = collection.find({ "key": { "$regex": "ScreenProbe$" }, "time": {"$gte": start, "$lt": end }})
    if includeBlanks or screenOnEntries.count() > 0:
        for data in screenOnEntries:
            dataValue = data["value"]
            screenOnCount += 1 if dataValue["screen_on"] else 0
        normalized = float(screenOnCount) / hours

        focus =  { "start": start, "end": end, "focus": normalized }

        if answerlistCollection is not None:
            selfAssessed = selfAssessedScoreForTimeRange(answerlistCollection, start, end, "Focus")
            focus["selfAssessed"] = selfAssessed["value"]
        return focus
    return None

def socialForTimeRange(collection, start, end, includeBlanks = False, answerlistCollection=None):
    score = 0
    
    # Get bluetooth entries for mobile phones only (middle byte == 02)
    # Also, filter out entries that were far away (looking at signal strength > -75) This number just seemed to fit the data well
    # The rationale for the signal strength filtering is that we want to try and keep this to face-to-face interactions
    bluetoothEntries = collection.find({ "key": { "$regex": "BluetoothProbe$" }, "time": { "$gte": start, "$lt": end }})
    if includeBlanks or bluetoothEntries.count() > 0:
        bluetoothEntries = [bt["value"] for bt in bluetoothEntries if "android-bluetooth-device-extra-class" in bt["value"] and bt["value"]["android-bluetooth-device-extra-class"]["mclass"] & 0x00FF00 == 512]
#        bluetoothEntries = [bt for bt in bluetoothEntries if bt["android-bluetooth-device-extra-rssi"] > -75]
        macKey = "android-bluetooth-device-extra-device"
        macs = set([bt[macKey]["maddress"] for bt in bluetoothEntries])
        btByPerson = [float(len([bt for bt in bluetoothEntries if bt[macKey]["maddress"] == mac])) for mac in macs]
        totalBt = sum(btByPerson)
        frequencies = [count / totalBt for count in btByPerson]
        score += sum([-frequency * math.log(frequency, 10) for frequency in frequencies]) * 10
        
    # For now, we're just taking the most recent probe value and checking message / call dates within it
    # This will not account for messages or call log entries that might have been deleted.

    # NOTE: we're including the start date in the queries below to simply shrink the number of entries we need to sort
    # Given that SMS and call log probes may include all messages and calls stored on the phone, we can't just look
    # at entries collected during that time frame

#    smsEntries = collection.find({ "key": { "$regex": "SmsProbe$" }, "time": {"$gte": start}})
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
    #print collection
    #pdb.set_trace()

    callLogEntries = collection.find({ "key": { "$regex": "CallLogProbe$" }, "time": {"$gte": start}})

    if includeBlanks or callLogEntries.count() > 0 or score > 0:
        callSets = [callEntry["value"] for callEntry in callLogEntries]
        #v4 = "calls" not in callSets[0]
        callSets = [value["calls"] if "calls" in value else value for value in callSets]
        calls = []
        for callSet in callSets:
            if isinstance(callSet, list):
                calls.extend(callSet)
            else:
                calls.append(callSet)
        calls = [call for call in calls if call["date"] >= start*1000 and call["date"] < end*1000]

        #callTimes = set([call["date"] for call in calls if call["date"] >= start*1000 and call["date"] < end*1000])
        countsByNumber = [float(len([call for call in calls if call["number"] == numberHash])) for numberHash in set([call["number"] for call in calls])]
        totalCalls = sum(countsByNumber)
        frequencies = [count / totalCalls for count in countsByNumber]
        score += sum([-frequency * math.log(frequency, 10) for frequency in frequencies]) * 10

        score = min(score, 10)
        social = { "start": start, "end": end, "social": score}
        if answerlistCollection is not None:
            selfAssessed = selfAssessedScoreForTimeRange(answerlistCollection, start, end, "Social")
            social["selfAssessed"] = selfAssessed["value"]
        return social
    return None


def aggregateForAllUsers(answerKey, timeRanges, aggregator, includeBlanks = False, mean = None, dev = None):
    profiles = Profile.objects.all()
    aggregates = {}

    for profile in profiles:
#        if mean is None or dev is None:
        data = aggregateForUser(profile, answerKey, timeRanges, aggregator, includeBlanks)
#        else:
#            data = aggregateForUser(profile, answerKey, timeRanges, aggregator, includeBlanks, mean.get(profile.uuid), dev.get(profile.uuid))
        if data is not None and len(data) > 0:
            aggregates[profile.uuid] = data

    return aggregates

def aggregateForUser(profile, answerKey, timeRanges, aggregator, includeBlanks = False):
    aggregates = []
    
    #print profile.uuid
    #pdb.set_trace()
    dbName = getDBName(profile)
    collection = connection[dbName]["funf"]
    answerlistCollection = connection[dbName]["answerlist"]
    
    for (start, end) in timeRanges:
        data = aggregator(collection, start, end)
        if data is not None:
            aggregates.append(aggregator(collection, start, end, includeBlanks, answerlistCollection))
    
    if answerKey is not None:
        saveAnswer(profile, answerKey, aggregates)

    return aggregates

def saveAnswer(profile, answerKey, data):
    dbName = getDBName(profile)
    collection = connection[dbName]["answerlist"]

    answer = collection.find({ "key": answerKey })
    if answer.count() == 0:
        answer = { "key": answerKey }
    else:
        answer = answer[0]
    
    answer["value"] = data
    collection.save(answer)

def getStartTime(daysAgo, startAtMidnight):
    currentTime = time.time()
    return time.mktime((date.fromtimestamp(currentTime) - timedelta(days=daysAgo)).timetuple()) if startAtMidnight else currentTime - daysAgo * 24 * 3600

def recentActivityLevels(includeBlanks = False):
    startTime = getStartTime(6, True)
    endTime = time.time()
    interval = 3600*2
    answerKey = "RecentActivityByHour"
    timeRanges = [(start, start + interval) for start in range(int(startTime), int(endTime), interval)]
    #pdb.set_trace()
    return aggregateForAllUsers(answerKey, timeRanges, activityForTimeRange, includeBlanks)

def recentFocusLevels(includeBlanks = False, means = None, devs = None):
    currentTime = time.time()
    answerKey = "RecentFocusByHour"
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=6)).timetuple())
    timeRanges = [(start, start + 3600*4) for start in range(int(startTime), int(currentTime), 3600*4)]
    data = aggregateForAllUsers(None, timeRanges, focusForTimeRange, includeBlanks)
 
    for uuid, focusList in data.iteritems():
        if len(focusList) > 0:
            data[uuid] = []
            if means is not None and devs is not None and uuid in means and uuid in devs:
                mean = means[uuid] if means[uuid] > 0 else 1
                dev = devs[uuid] if devs[uuid] > 0 else 1
                for f in focusList:
                    f["focus"] = 10.0*(1.0 - CDF(f["focus"], mean, dev))
                    data[uuid].append(f)                
            else:
                for f in focusList:
                    f["focus"] = int(f["focus"])
                    data[uuid].append(f)               
            profile = Profile.objects.get(uuid = uuid)
            saveAnswer(profile, answerKey, data[uuid]) 
    return data

def recentSocialLevels(includeBlanks = False):
    currentTime = time.time()
    answerKey = "RecentSocialByHour"
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=6)).timetuple())
    timeRanges = [(start, start + 3600*4) for start in range(int(startTime), int(currentTime), 3600*4)]
    data = aggregateForAllUsers(answerKey, timeRanges, socialForTimeRange, includeBlanks)
    
    return data

def recentActivityScore():
    #data = recentActivityLevels(False)
    currentTime = time.time()
    data = aggregateForAllUsers(None, [(currentTime - 3600 * 24 * 7, currentTime)], activityForTimeRange, False)
    score = {}
   
    for uuid, activityList in data.iteritems():
        if len(activityList) > 0:
            score[uuid] = computeActivityScore(activityList)
    
    return score

def recentFocusScore():
    data = recentFocusLevels(True)
    #currentTime = time.time()
    #data = aggregateForAllUsers(None, [(currentTime - 3600 * 24 * 7, currentTime)], focusForTimeRange, False)
    score = {}

    screenOnAverages = { uuid: float(sum([f["focus"] for f in focusList])) / len(focusList)  for uuid, focusList in data.iteritems()}
    screenOnStdDevs = { uuid: math.sqrt(sum([(f["focus"] - screenOnAverages[uuid])**2 for f in focusList]) / len(focusList)) for uuid, focusList in data.iteritems()}
    data = recentFocusLevels(True, screenOnAverages, screenOnStdDevs)
    
    for uuid, focusList in data.iteritems():
        if len(focusList) > 0:
            score[uuid] = computeFocusScore(focusList)
    
    return score

def recentSocialScore():
    data = recentSocialLevels(True)
    #currentTime = time.time()
    #data = aggregateForAllUsers(None, [(currentTime - 3600 * 24 * 7, currentTime)], socialForTimeRange, False)
    score = {}

    for uuid, socialList in data.iteritems():
        if len(socialList) > 0:
            score[uuid] = computeSocialScore(socialList)
    
    return score

def addNotification(profile, notificationType, title, content, uri):
    notification, created = Notification.objects.get_or_create(datastore_owner=profile, type=notificationType)
    notification.title = title
    notification.content = content
    notification.datastore_owner = profile
    if uri is not None:
        notification.uri = uri
    notification.save()

def addNotificationAndNotify(profile, notificationType, title, content, uri):
    addNotification(profile, notificationType, title, content, uri)
    if Device.objects.filter(datastore_owner = profile).count() > 0:
        gcm = GCM(settings.ASSISTANT_GCM_API_KEY)

        for device in Device.objects.filter(datastore_owner = profile):
            try:
                gcm.plaintext_request(registration_id=device.gcm_reg_id, data= {"action":"notify"})
            except Exception as e:
                print "Issue with sending notification to: %s, %s" % (profile.id, profile.uuid)
                print e

def notifyAll():
    for profile in Profile.objects.all():
        if Device.objects.filter(datastore_owner = profile).count() > 0:
            gcm = GCM(settings.ASSISTANT_GCM_API_KEY)
            for device in Device.objects.filter(datastore_owner = profile):
                try:
                    gcm.plaintext_request(registration_id=device.gcm_reg_id, data={"action":"notify"})
                except Exception as e:
                    print "Issue with sending notification to: %s, %s" % (profile.id, profile.uuid)
                    print e

def broadcastNotification(notificationType, title, content, uri):
    for profile in Profile.objects.all():
        addNotificationAndNotify(profile, notificationType, title, content, uri)



@task() 
def checkDataAndNotify():
    profiles = Profile.objects.all()
    data = {}
    
    currentTime = time.time()
    recentTime = currentTime - 24 * 3600  
    
    for profile in profiles:
        dbName = getDBName(profile)
        collection = connection[dbName]["funf"]
        newNotifications = False
       
        recentEntries = collection.find({ "time": {"$gte": recentTime }})
        
        if (recentEntries.count() == 0):
            addNotification(profile, 1, "Stale behavioral data", "Analysis may not accurately reflect your behavior.", None)
            newNotifications = True
        #addNotification(profile, 2, "Survey", "Take this survey", "/survey/?survey=1");
        #newNotifications = True
        if (newNotifications and Device.objects.filter(datastore_owner = profile).count() > 0):
            gcm = GCM(settings.GCM_API_KEY)
            #addNotification(profile, 2, "Push successful", "Push notifications are working properly.")
            for device in Device.objects.filter(datastore_owner = profile):
                #pdb.set_trace() 
                gcm.plaintext_request(registration_id=device.gcm_reg_id,data= { "action":"notify" })


            
@task() 
def ensureFunfIndexes():
    profiles = Profile.objects.all()

    for profile in profiles:
        dbName = getDBName(profile)
        collection = connection[dbName]["funf"]
        collection.ensure_index([("time", -1), ("key", 1)], cache_for=7200, background=True, unique=True, dropDups=True)

@task()
def recentSocialHealthScores():
    profiles = Profile.objects.all()
    data = {}
    
    activityScores = recentActivityScore()
    socialScores = recentSocialScore()
    focusScores = recentFocusScore()

    scoresList = [activityScores.values(), socialScores.values(), focusScores.values()]
    print scoresList
#    scoresList = [[d for d in scoreList if d > 0.0] for scoreList in scoresList]
    averages = [sum(scores) / len(scores) if len(scores) > 0 else 0 for scores in scoresList]
    variances = [map(lambda x: (x - averages[i]) * (x - averages[i]), scoresList[i]) for i in range(len(scoresList))]
    stdDevs = [math.sqrt(sum(variances[i]) / len(scoresList[i])) for i in range(len(scoresList))]

    activityStdDev = stdDevs[0]
    socialStdDev = stdDevs[1]
    focusStdDev = stdDevs[2]
  
    print averages
    print stdDevs 

    for profile in [p for p in profiles if p.uuid in activityScores.keys()]:
        print "storing %s" % profile.uuid
        dbName = getDBName(profile) 
        collection = connection[dbName]["answerlist"]
        
        answer = collection.find({ "key" : "socialhealth" })
        answer = answer[0] if answer.count() > 0 else {"key": "socialhealth", "value":[]} 
        
        #data[profile.uuid] = [datum for datum in answer["value"] if datum["layer"] != "User"]
        data[profile.uuid] = []
        #pdb.set_trace()
        data[profile.uuid].append({ "key": "activity", "layer": "User", "value": activityScores.get(profile.uuid, 0) })
        data[profile.uuid].append({ "key": "social", "layer": "User", "value": socialScores.get(profile.uuid, 0) })
        data[profile.uuid].append({ "key": "focus", "layer": "User", "value": focusScores.get(profile.uuid, 0)  })
        data[profile.uuid].append({ "key": "activity", "layer": "averageLow", "value": max(0, averages[0] - stdDevs[0])})
        data[profile.uuid].append({ "key": "social", "layer": "averageLow", "value": max(0, averages[1] - stdDevs[1]) })
        data[profile.uuid].append({ "key": "focus", "layer": "averageLow", "value": max(0, averages[2] - stdDevs[2]) })
        data[profile.uuid].append({ "key": "activity", "layer": "averageHigh", "value": min(averages[0] + stdDevs[0], 10) })
        data[profile.uuid].append({ "key": "social", "layer": "averageHigh", "value": min(averages[1] + stdDevs[1], 10) })
        data[profile.uuid].append({ "key": "focus", "layer": "averageHigh", "value": min(averages[2] + stdDevs[2], 10) })

        answer["value"] = data[profile.uuid]
        
        collection.save(answer)

    # After we're done, re-compute the time graph data to include zeros for blanks
    # not ideal to compute this twice, but it gets the job done
    recentActivityLevels(True)
    # Purposely excluding social and focus scores - blanks are includede in their calculations as blank could imply actual zeroes, rather than missing data
    #recentSocialLevels(True)
    #recentFocusLevels(True)
    return data

def distanceBetweenLatLongs(latlong1, latlong2):  
    earthRadius = 6371 # km
    dLat = math.fabs(math.radians(latlong2[0] - latlong1[0]))
    dLong = math.fabs(math.radians(latlong2[1] - latlong1[1]))
    lat1 = math.radians(latlong1[0])
    lat2 = math.radians(latlong2[0])
    dLatSin = math.sin(dLat / 2.0)
    dLongSin = math.sin(dLong / 2.0)
    a = dLatSin*dLatSin + dLongSin*dLongSin*math.cos(lat1)*math.cos(lat2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return earthRadius * c * 1000 # Converting to meters here... more useful for our purposes than km

def boxContainsPoint(box, point):
    return box[0] <= point[0] <= box[2] and box[1] <= point[1] <= box[3] 

def boundsOverlap(bounds1, bounds2):
    points1 = [(x, y) for x in bounds1[::2] for y in bounds1[1::2]]
    points2 = [(x, y) for x in bounds2[::2] for y in bounds2[1::2]]
    
    for point in points1:
        if boxContainsPoint(bounds2, point):
            return True

    for point in points2:
        if boxContainsPoint(bounds1, point):
            return True

    return False

def mergeBoxes(bounds1, bounds2):
    return [min(bounds1[0], bounds2[0]), min(bounds1[1], bounds2[1]), max(bounds1[2], bounds2[2]), max(bounds1[3], bounds2[3])]

def centroid(points):
    if len(points) == 0:
        return (0,0)
    sums = reduce(lambda x,y: (x[0] + y[0], x[1] + y[1]), points, (0,0))
    return (sums[0] / len(points), sums[1] / len(points))

def findRecentPlaceBounds(recentPlaceKey, timeRanges):
    profiles = Profile.objects.all()
    data = {}
    
    for profile in profiles:
        dbName = getDBName(profile)
        collection = connection[dbName]["funf"]
        locations = []

        # An explanation for why we're doing things the way we are below 
        # (there are a few obvious strategies for finding places in location data):
        # 1)  Naive approach - take all location samples in all time ranges, find clusters within them, 
        #     take the one with the most points in it.
        # 2)  Faster, but more complicated - do 1) for each time range individually to get candidate regions. 
        #     Loop over candidate regions, collapsing and "voting" for those that overlap. Take the one with the most votes.
        #     Notes: This is essentially 2-levels of clustering with the simplification that overlapping regions would 
        #     have been clustered together anyway (ie; bounding boxes should be similar, but not the same, as strategy 1)
        #     Pros: Faster - each clustering is limited to 100 entries. In practice, this is more than enough. 
        #         If this poses an issue, time ranges can be chosen more carefully (more / shorter time ranges)
        #     Cons: Bounding boxes aren't the same as 1). In particular, two candidate boxes may not overlap, but should 
        #         have been clustered together anyway.
        # 3)  Binning pre-process - Same as 1), but perform a binning pre-process on the location data, collapsing multiple 
        #     samples into single entries, with associaated weights.
        #     Notes: This is essentially a lower-resolution version of strategy 1. Bounding boxes should be lower-resolution
        #     versions of those from strategy 1. 
        #     Pros: Bounding boxes should be the same as #1. Takes into account all entries when clustering. 
        #     Cons: Less fine-grained control over the number of entries per cluster than #2. In particular, for sparse 
        #         location data, this may not reduce the number of entries we must cluster.
        # The following is an implementation of method #2:
        potentialRegions = []
        #pdb.set_trace()
        for timeRange in timeRanges:
            values = [entry["value"] for entry in collection.find({ "key": { "$regex": "LocationProbe$"}, "time": { "$gte": timeRange[0], "$lt": timeRange[1]}}, limit=100)]
            # Use all locations except the most gratuitously inaccurate ones
            values = [value for value in values if float(value["maccuracy"]) < 100]
            clusters = clusterFunfLocations(values, 100)
            if (len(clusters) > 0):
                clusterLocations = max(clusters, key= lambda cluster: len(cluster))
                if isinstance(clusterLocations, list):
                    workLats = [loc[0] for loc in clusterLocations]
                    workLongs = [loc[1] for loc in clusterLocations]
                    potentialRegions.append([min(workLats), min(workLongs), max(workLats), max(workLongs)])
      
        if len(potentialRegions) > 0: 
            overlaps = [{ "region" : r1, "overlapList": [r2 for r2 in potentialRegions if r2 is not r1 and boundsOverlap(r1, r2)]} for r1 in potentialRegions]
            mostOverlap = max(overlaps, key = lambda entry: len(entry["overlapList"]))
            mostVoted = reduce(lambda r1, r2: mergeBoxes(r1, r2), mostOverlap["overlapList"], mostOverlap["region"])
            
            answerlistCollection = connection[dbName]["answerlist"]
            answer = answerlistCollection.find({ "key" : "RecentPlaces" })
            answer = answer[0] if answer.count() > 0 else {"key": "RecentPlaces", "value":[]}
            data[profile.uuid] = [datum for datum in answer["value"] if datum["key"] != recentPlaceKey]
            data[profile.uuid].append({ "key": recentPlaceKey, "bounds": mostVoted})
            answer["value"] = data[profile.uuid]
            answerlistCollection.save(answer)
    return data

def clusterFunfLocations(values, distance):
    potentialRegions = []
    values = [value["location"] if "location" in value else value for value in values]
    latlongs = [(value["mlatitude"], value["mlongitude"]) for value in values]
    clustering = cluster.HierarchicalClustering(latlongs, distanceBetweenLatLongs)
    clusters = clustering.getlevel(distance)    
    return clusters

def findRecentLocations():
    currentTime = time.time()
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=3)).timetuple())
    sampleTimes = range(int(startTime),int(currentTime), 8*3600)

    data = {}

    profiles = Profile.objects.all()

    for profile in profiles:
        dbName = getDBName(profile) 
        collection = connection[dbName]["funf"]
        answerlistCollection = connection[dbName]["answerlist"]
        answerlistCollection.remove({"key":"RecentLocations"})
        answer = answerlistCollection.find({ "key": "RecentLocations" })
        answer = answer[0] if answer.count() > 0 else { "key": "RecentLocations", "value":[]}
        data[profile.uuid] = []

        clusters = []
        for sampleTime in sampleTimes:
            sampleNumber = int(sampleTime - startTime) / 3600
            locationKey = str(sampleNumber) + "-" + str(sampleNumber + 1)
            values = [entry["value"] for entry in collection.find({ "key": { "$regex": "LocationProbe$"}, "time": { "$gte": sampleTime, "$lt": sampleTime + 8*3600}}, limit = 100)]
            values = [value for value in values if float(value["maccuracy"]) < 30]
            clusters = clusterFunfLocations(values, 20)
            #We're only interested in places that have more than 3 samples - either the users stayed there a while, or returned there a number of times)
            clusters = [cluster for cluster in clusters if len(cluster) > 3]
            centroids = [centroid(cluster) for cluster in clusters]
            if len(centroids) > 0:
                data[profile.uuid].append({ "key": locationKey, "points": centroids})
        
        answer["value"] = data[profile.uuid]
        answerlistCollection.save(answer)
    
    return data

@task()
def createUserRecord():
    currentTime = time.time()
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=1)).timetuple())

    socialHealthScores = recentSocialHealthScores()
    data = {}

    for guid, scores in socialHealthScores.iteritems():
        profile = Profile.objects.get(uuid = guid)
        dbName = getDBName(profile)
        data[guid] = {}
        collection = connection[dbName]["funf"]
        answerCollection = connection[dbName]["answer"]
        answerCollection.remove({"key":"UserRecord"})
        averageLows = {score["key"] : score["value"] for score in scores if score["layer"] == "averageLow"}
        averageHighs = {score["key"] : score["value"] for score in scores if score["layer"] == "averageHigh"}
        userScores = {score["key"] : score["value"] for score in scores if score["layer"] == "User"}
        print averageLows
        print averageHighs
        print userScores
        color = "none"
        color_fill = "#9ACD32"
        for metric, value in userScores.iteritems():
            if value < averageLows[metric] or value > averageHighs[metric]:
                color_fill = "#FF0000"
                color = "red"
        locations = [entry["value"] for entry in collection.find({ "key": { "$regex": "LocationProbe$"}, "time": { "$gte": startTime, "$lt": currentTime}}, limit = 200)]
        locations = [value["location"] if "location" in value else value for value in locations]
        
        timestampedlatlongs = [{ "timestamp":int(value["timestamp"]), "lat":value["mlatitude"], "lng":value["mlongitude"]} for value in locations]
        data[guid]["user"] = "Name"
        data[guid]["color"] = color
        data[guid]["color-fill"] = color_fill
        data[guid]["locations"] = timestampedlatlongs
        data[guid]["issharing"] = False
        data[guid]["photo"] = "/static/img/bbc_demo/locked.png"
        answer = { "key":"UserRecord"}
        answer["value"] = data[guid]
        answerCollection.save(answer)
    return data


@task()
def findRecentPlaces():
    currentTime = time.time()
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=6)).timetuple())

    # Note: we're not taking the full 9-5 sampling. Clustering is expensive, so anything we can leave out helps...
    # Combined with the fact that "lunch" time might not be indicative of work locations, this might be more accurate anyway       
    nineToFives = [(nine, nine + 3600*8) for nine in range(int(startTime + 3600*9), int(currentTime), 3600*24)]
    #nineToFives.extend([(two, two + 3600*2) for two in range(int(startTime + 3600*14), int(currentTime), 3600*24)])

    
    #print "Finding work locations..."       
    data = findRecentPlaceBounds("work", nineToFives)
    midnightToSixes = [(midnight, midnight + 3600*6) for midnight in range(int(startTime), int(currentTime), 3600* 24)]

    #print "Finding home locations..."
    data = findRecentPlaceBounds("home", midnightToSixes)

    return data

@task()
def estimateTimes():
    profiles = Profile.objects.all()
    currentTime = time.time()
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=7)).timetuple())
    
    for profile in profiles:
        dbName = getDBName(profile) 
        answerListCollection = connection[dbName]["answerlist"]
        funf = connection[dbName]["funf"]
        recentPlaces = answerListCollection.find({ "key": "RecentPlaces" })
        startTimes = { }
        endTimes = { }
        if recentPlaces.count() > 0:
            recentPlaces = recentPlaces[0]
            print recentPlaces["value"]
            for place in [p for p in recentPlaces["value"]]:
                print place
                placeKey = place["key"]
                startTimes[placeKey] = []
                endTimes[placeKey] = []
                print profile.uuid, placeKey
                bounds = place["bounds"]
                for intervalStart in [t for t in range(int(startTime), int(time.mktime(today.timetuple())), 3600 * 24) if date.fromtimestamp(t).weekday() < 5]:
                    print intervalStart, intervalStart + 24*3600
                    locations = [(entry["time"], entry["value"]) for entry in funf.find({ "key": { "$regex": "LocationProbe$"}, "time": { "$gte": intervalStart, "$lt": intervalStart + 24*3600}}, limit = 1000)]
                    if len(locations) > 0:
                        print len(locations)
#                        workLocations = [(value[0], value[1]) for value in workLocations]
#                        pdb.set_trace()
                        locations = [(value[0], (value[1]["mlatitude"], value[1]["mlongitude"])) for value in locations]
                        atWork = [(loc[0], boxContainsPoint(bounds, loc[1])) for loc in locations]
                        deltas = reduce(lambda x, y: x + [y] if len(x) == 0 or x[-1][1] != y[1] else x, atWork, [])
                        #workTimes = [value[0] for value in workLocations if boxContainsPoint(work["bounds"], value[1])]
                        if len(deltas) > 1: 
                            if placeKey == "home":
                                print deltas
                                startTimes[placeKey].append(max([v[0] for v in deltas if not v[1]]) - intervalStart)
                                if 18000 < min([v[0] for v in deltas if v[1]]) - intervalStart < 72000:
                                    endTimes[placeKey].append(min([v[0] for v in deltas if v[1]]) - intervalStart)
                            else:
                                startTimes[placeKey].append(min([v[0] for v in deltas if not v[1]]) - intervalStart)
                                endTimes[placeKey].append(max([v[0] for v in deltas if v[1]]) - intervalStart)
                if len(startTimes[placeKey]) > 0 and len(endTimes[placeKey]) > 0:
                    averageStartTime = sum(startTimes[placeKey]) / (3600 * len(startTimes[placeKey]))
                    averageEndTime = sum(endTimes[placeKey]) / (3600 * len(endTimes[placeKey]))
                    recentPlaces["value"].remove(place)
                    place["start"] = averageStartTime
                    place["end"] = averageEndTime
                    recentPlaces["value"].append(place)
                    answerListCollection.save(recentPlaces)

@task()
def findSuggestedPlaces():
    profiles = Profile.objects.all()
    sparql = SPARQLWrapper("http://live.linkedgeodata.org/sparql")
    sparql.setReturnFormat(JSON)
    query = "Prefix lgdo: <http://linkedgeodata.org/ontology/> Select distinct ?placeUri From <http://linkedgeodata.org> { ?placeUri ?p ?o . ?placeUri rdfs:label ?l . ?placeUri geo:geometry ?g .Filter(bif:st_intersects (?g, bif:st_point (%s, %s), 0.5)) . }"

    for profile in profiles:
        dbName = getDBName(profile)
        answerListCollection = connection[dbName]["answerlist"]
        recentPlaceList = answerListCollection.find({ "key": "RecentPlaces" })
        suggestions = []
        if recentPlaceList.count() > 0:
            # There should only be one - ignore any others in the event of corrupt data
            
            recentPlaceList = recentPlaceList[0]
            print recentPlaceList
            for recentPlace in recentPlaceList["value"]:
                # We're taking only the upper-left corner for now to simplify things
                placeKey = recentPlace["key"]
                # NOTE: for legacy data, we still need to process this when generating the rdf...
                reason = "http://linkedpersonaldata.org/ontology#nearWork" if placeKey == "work" else "http://linkedpersonaldata.org/ontology#nearHome"
                bounds = recentPlace["bounds"]
                lat = bounds[0]
                lng = bounds[1]
                temp = query % (lng, lat)
                print temp
                sparql.setQuery(temp)
                results = sparql.query().convert()
                suggestions.extend([{ "reason": reason, "uri": result["placeUri"]["value"]} for result in results["results"]["bindings"]])
            suggestedPlaces = answerListCollection.find({ "key": "SuggestedPlaces" })
            suggestedPlaces = suggestedPlaces[0] if suggestedPlaces.count() > 0 else { "key": "SuggestedPlaces", "value": [] }
            suggestedPlaces["value"] = suggestions
            answerListCollection.save(suggestedPlaces)

@task() 
def findMusicGenres():
    profiles = Profile.objects.all()
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    artistQuery = "PREFIX dbpprop: <http://dbpedia.org/property/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> select ?artist ?genre from <http://dbpedia.org> where { ?artist rdfs:label \"%s\"@en . ?artist dbpprop:genre ?genre }" 
    albumQuery = "PREFIX dbpedia-owl: <http://dbpedia.org/ontology/> PREFIX dbpprop: <http://dbpedia.org/property/> select ?album ?genre from  <http://dbpedia.org> where { ?album a dbpedia-owl:Album . ?album dbpprop:name '%s'@en . ?album dbpprop:genre ?genre }"

    for profile in profiles:
        dbName = getDBName(profile) 
        answerListCollection = connection[dbName]["answerlist"]
        collection = connection[dbName]["funf"]
        
        songs = [song["value"] for song in collection.find({ "key": { "$regex": "AudioMediaProbe$"}})]
        artists = set([str(song["artist"]) for song in songs if str(song["artist"]) != "<unkown>" and '"' not in str(song["artist"])])
#        albums = set([str(song["album"]) for song in songs if str(song["album"]) != "<unknown>" and '"' not in str(song["album"])])
        genres = []
        for artist in artists:
            temp = artistQuery % artist
            print temp
            sparql.setQuery(temp)
            results = sparql.query().convert()
            genres.extend([binding["genre"]["value"] for binding in results["results"]["bindings"]])
#        for album in albums:
#            temp = albumQuery % album
#            print temp
#            sparql.setQuery(temp)
#            results = sparql.query().convert()
#            genres.extend([binding["genre"]["value"] for binding in results["results"]["bindings"]])
        if len(genres) > 0:
            counts = Counter(genres).most_common(10)
            musicGenres = answerListCollection.find({ "key": "MusicGenres" })
            musicGenres = musicGenres[0] if musicGenres.count() > 0 else { "key": "MusicGenres", "value": [] }
            musicGenres["value"] = [count[0] for count in counts]
            answerListCollection.save(musicGenres)



@task()
def dumpFunfData():
    profiles = Profile.objects.all()
    outputConnection = sqlite3.connect("oms_pds/static/dump.db")
    c = outputConnection.cursor()
    c.execute("DROP TABLE IF EXISTS funf;") 
    c.execute("CREATE TABLE funf (user_id integer, key text, time real, value text);")
    c.execute("CREATE INDEX funf_key_time_idx on funf(key, time)") 
    for profile in profiles:
        dbName = getDBName(profile)
        funf = connection[dbName]["funf"]
        user = int(profile.id)     
        for datum in funf.find():
            #print type(user), type(datum["key"]), type(datum["time"]), type(datum["value"])
            key = datum["key"]
            if key is not None:
                key = key[key.rfind(".") + 1:]
                c.execute("INSERT INTO funf VALUES (?,?,?,?);", (user,key,datum["time"],"%s"%datum["value"]))
    
    outputConnection.commit()
    outputConnection.close()

@task()
def dumpSurveyData():
    profiles = Profile.objects.all()
    outputConnection = sqlite3.connect("oms_pds/static/dump.db")
    c = outputConnection.cursor()
    c.execute("DROP TABLE IF EXISTS survey;")
    c.execute("CREATE TABLE survey (user_id integer, key text, time real, value text);")

    for profile in profiles:
        dbName = getDBName(profile)
        answerlist = connection[dbName]["answerlist"]
        user = int(profile.id)
        for datum in answerlist.find({ "key": { "$regex": "Past3Days$"}}):
            for answer in datum["value"]:
                #print type(user), type(datum["key"]), type(answer)#, type(datum["value"])
                c.execute("INSERT INTO survey VALUES (?,?,?,?);", (user,datum["key"],answer["time"],"%s"%answer["value"]))
        for datum in answerlist.find({ "key": { "$regex": "Verification"}}):
            for answer in datum["value"]:
                c.execute("INSERT INTO survey VALUES (?,?,?,?);", (user,datum["key"],answer["time"],"%s"%answer["value"]))
        for datum in answerlist.find({ "key": { "$regex": "Last15Minutes"}}):
            for answer in datum["value"]:
                c.execute("INSERT INTO survey VALUES (?,?,?,?);", (user,datum["key"],answer["time"],"%s"%answer["value"]))
    outputConnection.commit()
    outputConnection.close()

