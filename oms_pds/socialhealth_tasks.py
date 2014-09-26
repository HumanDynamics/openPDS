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
from oms_pds.pds.internal import getInternalDataStore
#from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
import sqlite3

"""the MONGODB_DATABASE_MULTIPDS setting is set by extract-user-middleware in cases where we need multiple PDS instances within one PDS service """


connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

ANSWERKEY_NAME_MAPPING = {
    "recentFocusByHour": "Focus",
    "recentSocialByHour": "Social",
    "recentActivityByHour": "Activity",
    "socialhealth": "My Social Health"
}

def copyData(fromInternalDataStore, toInternalDataStore):
    startTime = 1391291231
    endTime = 1392768449

    probes = ["LocationProbe", "ActivityProbe", "SmsProbe", "CallLogProbe", "BluetoothProbe", "WifiProbe", "ScreenProbe"]

    for probe in probes:
        for d in fromInternalDataStore.getData(probe, startTime, endTime):
            toInternalDataStore.saveData(d)

def LNPDF(x, loc, scale):
    return math.exp(-(math.log(x)-loc)**2/(2*(scale**2))) / (x*math.sqrt(2*math.pi)*scale)

def CDF(x, mean, dev):
    return 0.5 * (1 + math.erf((x - mean) / (dev * math.sqrt(2)))) if dev <> 0 else 0

def computeActivityScore(activityList):
    recentActiveTotals = [1.0 * float(item["low"]) + item["high"] for item in activityList]
    recentTotal = float(sum([item["total"] for item in activityList]))
     
    factor = 1000.0 / recentTotal if recentTotal > 0 else 1
    activeTotal = factor * float(sum(recentActiveTotals))
    return min(10.0 * CDF(activeTotal, 54, 39), 10)

def computeFocusScore(focusList):
    recentTotals = [item["focus"] for item in focusList]
    x = float(sum(recentTotals))
    return min(10.0 * CDF(float(sum(recentTotals)), 184.5, 88), 10)

def computeSocialScore(socialList):
    recentTotals = [item["social"] for item in socialList]
    return min(10.0 * CDF(float(sum(recentTotals)), 68.8, 68.8), 10)

def intervalsOverlap(i1, i2):
    return i2[0] <= i1[0] <= i2[1] or i2[0] <= i1[1] <= i2[1] or i1[0] <= i2[0] <= i1[1] or i1[0] <= i2[1] <= i1[1]

def selfAssessedScoreForTimeRange(internalDataStore, start, end, metric):
    verificationEntries = internalDataStore.getAnswerList({ "key": metric + "Verification"})
    past3DaysEntries = internalDataStore.getAnswerList({ "key": metric + "Past3Days" })
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


def activityForTimeRange(internalDataStore, start, end, includeBlanks = False, includeSelfAssessed = False):
    lowActivityIntervals = highActivityIntervals = totalIntervals = 0

    activityEntries = internalDataStore.getData("ActivityProbe", start, end)
    if activityEntries is not None and (includeBlanks or activityEntries.count() > 0):        
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
        if includeSelfAssessed:
            selfAssessed = selfAssessedScoreForTimeRange(internalDataStore, start, end, "Activity")
            activity["selfAssessed"] = selfAssessed["value"]
        return activity
    return None

def focusForTimeRange(internalDataStore, start, end, includeBlanks = False, includeSelfAssessed = False):
    screenOnCount = 0
    hours = float((end - start)) / 3600.0

    screenOnEntries = internalDataStore.getData("ScreenProbe", start, end)
    if screenOnEntries is not None and (includeBlanks or screenOnEntries.count() > 0):
        for data in screenOnEntries:
            dataValue = data["value"]
            screenOnCount += 1 if dataValue["screen_on"] else 0
        normalized = float(screenOnCount) / hours

        focus =  { "start": start, "end": end, "focus": normalized }

        if includeSelfAssessed:
            selfAssessed = selfAssessedScoreForTimeRange(internalDataStore, start, end, "Focus")
            focus["selfAssessed"] = selfAssessed["value"]
        return focus
    return None

def socialForTimeRange(internalDataStore, start, end, includeBlanks = False, includeSelfAssessed = False):
    score = 0
    
    # Get bluetooth entries for mobile phones only (middle byte == 02)
    # Also, filter out entries that were far away (looking at signal strength > -75) This number just seemed to fit the data well
    # The rationale for the signal strength filtering is that we want to try and keep this to face-to-face interactions
    bluetoothEntries = internalDataStore.getData("BluetoothProbe", start, end)
    if bluetoothEntries is not None and (includeBlanks or bluetoothEntries.count() > 0):
        bluetoothEntries = [bt["value"] for bt in bluetoothEntries if "android-bluetooth-device-extra-class" in bt["value"] and bt["value"]["android-bluetooth-device-extra-class"]["mclass"] & 0x00FF00 == 512]
#        bluetoothEntries = [bt for bt in bluetoothEntries if bt["android-bluetooth-device-extra-rssi"] > -75]
        macKey = "android-bluetooth-device-extra-device"
        macs = set([bt[macKey]["maddress"] for bt in bluetoothEntries])
        btByPerson = [float(len([bt for bt in bluetoothEntries if bt[macKey]["maddress"] == mac])) for mac in macs]
        totalBt = sum(btByPerson)
        frequencies = [count / totalBt if totalBt > 0 else 1 for count in btByPerson]
        score += sum([-frequency * math.log(frequency, 10) for frequency in frequencies]) * 10
        
    # For now, we're just taking the most recent probe value and checking message / call dates within it
    # This will not account for messages or call log entries that might have been deleted.

    # NOTE: we're including the start date in the queries below to simply shrink the number of entries we need to sort
    # Given that SMS and call log probes may include all messages and calls stored on the phone, we can't just look
    # at entries collected during that time frame
    smsEntries = internalDataStore.getData("SmsProbe", start, None)
    
    if smsEntries is not None and (includeBlanks or smsEntries.count() > 0 or score > 0):
        # Message times are recorded at the millisecond level. It should be safe to use that as a unique id for messages        
        messages = [smsEntry["value"] for smsEntry in smsEntries]
        messages = [message for message in messages if message["date"] >= start*1000 and message["date"] < end*1000]
        
        # We're assuming a hit on a thread is equivalent to a single phone call
        messageCountByThread = []
        
        for threadId in set([message["thread_id"] for message in messages]):
            smsCount = float(len([message for message in messages if message["thread_id"] == threadId]))
            messageCountByThread.append(smsCount)

        totalSms = sum(messageCountByThread)
        frequencies = [count / totalSms if totalSms > 0 else 1 for count in messageCountByThread]
        score += sum([-frequency * math.log(frequency, 10) for frequency in frequencies]) * 10

    #print collection
    #pdb.set_trace()

    callLogEntries = internalDataStore.getData("CallLogProbe", start, end)

    if callLogEntries is not None and (includeBlanks or callLogEntries.count() > 0 or score > 0):
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
        frequencies = [count / totalCalls if totalCalls > 0 else 1 for count in countsByNumber]
        score += sum([-frequency * math.log(frequency, 10) for frequency in frequencies]) * 10

        score = min(score, 10)
        social = { "start": start, "end": end, "social": score}
        if includeSelfAssessed:
            selfAssessed = selfAssessedScoreForTimeRange(internalDataStore, start, end, "Social")
            social["selfAssessed"] = selfAssessed["value"]
        return social
    return None


def aggregateForAllUsers(answerKey, timeRanges, aggregator, serviceId, includeBlanks = False, mean = None, dev = None):
    profiles = Profile.objects.all()
    aggregates = {}

    for profile in profiles:
        # NOTE: need a means of getting at a token for authorizing this task to run. For now, we're not checking anyway, so it's blank
        internalDataStore = getInternalDataStore(profile, "MGH smartCATCH", "Social Health Tracker", "")
#        if mean is None or dev is None:
        data = aggregateForUser(internalDataStore, answerKey, timeRanges, aggregator, includeBlanks)
#        else:
#            data = aggregateForUser(profile, answerKey, timeRanges, aggregator, includeBlanks, mean.get(profile.uuid), dev.get(profile.uuid))
        if data is not None and len(data) > 0:
            aggregates[profile.uuid] = data

    return aggregates

def aggregateForUser(internalDataStore, answerKey, timeRanges, aggregator, includeBlanks = False):
    aggregates = []
    
    for (start, end) in timeRanges:
        data = aggregator(internalDataStore, start, end)
        if data is not None:
            aggregates.append(aggregator(internalDataStore, start, end, includeBlanks))
    
    if answerKey is not None:
        internalDataStore.saveAnswer(answerKey, aggregates)

    return aggregates

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
    return aggregateForAllUsers(answerKey, timeRanges, activityForTimeRange, "Activity", includeBlanks)

def recentFocusLevels(includeBlanks = False, means = None, devs = None):
    currentTime = time.time()
    answerKey = "RecentFocusByHour"
    today = date.fromtimestamp(currentTime)
    startTime = time.mktime((today - timedelta(days=6)).timetuple())
    timeRanges = [(start, start + 3600*4) for start in range(int(startTime), int(currentTime), 3600*4)]
    data = aggregateForAllUsers(None, timeRanges, focusForTimeRange, "Focus", includeBlanks)
 
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
            # TODO: get a token here to run internal queries against...
            ids = getInternalDataStore(profile, "MGH smartCATCH", "Social Health Tracker", "")
            ids.saveAnswer(answerKey, data[uuid]) 
    return data

def recentSocialLevels(includeBlanks = False):
    answerKey = "RecentSocialByHour"
    currentTime = time.time()
    startTime = getStartTime(6, True)
    timeRanges = [(start, start + 3600*4) for start in range(int(startTime), int(currentTime), 3600*4)]
    data = aggregateForAllUsers(answerKey, timeRanges, socialForTimeRange, "Social", includeBlanks)
    
    return data

def recentSocialLevels2(internalDataStore, includeBlanks = False):
    answerKey = "RecentSocialByHour"
    currentTime = time.time()
    starttime = getStartTime(6, True)
    timeRanges = [(start, start + 3600*4) for start in range(int(startTime), int(currentTime), 3600*4)]
    data = aggregateForUser(internalDataStore, answerKey, timeRanges, socialForTimeRange, "Social", includeBlanks)

    return data


def recentActivityScore():
    #data = recentActivityLevels(False)
    currentTime = time.time()
    data = aggregateForAllUsers(None, [(currentTime - 3600 * 24 * 7, currentTime)], activityForTimeRange, "Activity", False)
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

    screenOnAverages = { uuid: float(sum([f["focus"] for f in focusList])) / len(focusList) if len(focusList) > 0 else 0  for uuid, focusList in data.iteritems()}
    screenOnStdDevs = { uuid: math.sqrt(sum([(f["focus"] - screenOnAverages[uuid])**2 for f in focusList]) / len(focusList)) if len(focusList) > 0 else 0 for uuid, focusList in data.iteritems()}
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


# formats a notification the way the SmartCATCH client understands it
def formatNotification(question, type="Picker", description="", items=[], **kwargs):
    s1 = "<startTitle>" + question + "<endTitle><startType>" + type + "<endType><startDescription>" + description + "<endDescription>"
    s2 = "<startNumItems>%d<endNumItems>" % len(items) + ''.join(["<startI%d>%s<endI%d>" % (i+1,items[i],i+1) for i in xrange(len(items))])
    s3 = "<startNegButton>Delay<endNegButton><startPosButton>Submit<endPosButton><startNumRepeats>3<endNumRepeats><startTimeRepeat>5000<endTimeRepeat>" # TODO: format this. Unclear about this param$

    return json.dumps({ 's1': s1, 's2': s2, 's3': s3 })
#    return s1, s2, s3 # TODO: JSONfy

@task()
def smartcatchNotifications():
    print "Starting notifications task"

    profiles = Profile.objects.all()
    for profile in profiles:

	    if Device.objects.filter(datastore_owner = profile).count() > 0:
        	gcm = GCM(settings.GCM_API_KEY)
	        for device in Device.objects.filter(datastore_owner = profile):
        	    try:
                	# add the notification to the DB
	                q = 'How are you today?'
        	        js = formatNotification(q, description='A query about your emotional state', items=['Low','Medium','High'])
                	addNotification(profile, 2, 'SmartCATCH', q, js)
	                # send an alert that a notification is ready (app will call back to fetch the notification data)
        	        print "id=%s, uuid=%s, device=%s" % (profile.id, profile.uuid,device.gcm_reg_id)
                	gcm.plaintext_request(registration_id=device.gcm_reg_id, data={"action":"notify"})
	            except Exception as e:
        	        print "Issue with sending notification to: %s, %s" % (profile.id, profile.uuid)
                	print e    

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
 
    print "Averages (activity, social, focus):" 
    print averages
    print "Standard Deviations (activity, social, focus):"
    print stdDevs 

    for profile in [p for p in profiles if p.uuid in activityScores.keys()]:
        print "storing %s" % profile.uuid
        
        internalDataStore = getInternalDataStore(profile, "MGH smartCATCH", "Social Health Tracker", "")
 
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

        internalDataStore.saveAnswer("socialhealth", data[profile.uuid])

    # After we're done, re-compute the time graph data to include zeros for blanks
    # not ideal to compute this twice, but it gets the job done
    recentActivityLevels(True)
    # Purposely excluding social and focus scores - blanks are includede in their calculations as blank could imply actual zeroes, rather than missing data
    #recentSocialLevels(True)
    #recentFocusLevels(True)
    return data

def getToken(profile, app_uuid):
    return ""

@task()
def recentSocialHealthScores2():
    profiles = Profile.objects.all()
    startTime = getStartTime(6, True)
    currentTime = time.time()
    timeRanges = [(start, start + 3600*4) for start in range(int(startTime), int(currentTime), 3600*4)]

    sums = {"activity": 0, "social": 0, "focus": 0}
    activeUsers = []
    data = {}

    for profile in profiles:
        token = getToken(profile, "app-uuid")
        internalDataStore = getInternalDataStore(profile, "MGH smartCATCH", "Social Health Tracker", token)

        activityLevels = aggregateForUser(internalDataStore, "RecentActivityByHour", timeRanges, activityForTimeRange, False)
       
        if len(activityLevels) > 0:
            socialLevels = aggregateForUser(internalDataStore, "RecentSocialByHour", timeRanges, socialForTimeRange, True)
            focusLevels = aggregateForUser(internalDataStore, "RecentFocusByHour", timeRanges, focusForTimeRange, True)

            activityScore = computeActivityScore(activityLevels)
            socialScore = computeSocialScore(socialLevels)
            focusScore = computeFocusScore(focusLevels)
    
            sums["activity"] += activityScore
            sums["social"] += socialScore
            sums["focus"] += focusScore
            activeUsers.append(profile)
    
            data[profile.uuid] = {}
            data[profile.uuid]["user"] = {
                "activity": activityScore,
                "social": socialScore,
                "focus": focusScore
            } 

    numUsers = len(activeUsers)
    if numUsers > 0:
        averages = { k: sums[k] / numUsers for k in sums }
        variances = { k: [(data[p.uuid]["user"][k] - averages[k])**2 for p in activeUsers] for k in averages }
        stdDevs = { k: math.sqrt(sum(variances[k]) / len(variances[k])) for k in variances }
        for profile in activeUsers:
            token = getToken(profile, "app-uuid")
            internalDataStore = getInternalDataStore(profile, "MGH smartCATCH", "Social Health Tracker", token)
            data[profile.uuid]["averageLow"] = { k: max(0, averages[k] - stdDevs[k]) for k in stdDevs }
            data[profile.uuid]["averageHigh"] = { k: min(averages[k] + stdDevs[k], 10) for k in stdDevs }
            internalDataStore.saveAnswer("socialhealth", data[profile.uuid])
    return data
