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
import socialhealth_tasks

# probes: CallLogProbe, WifiProbe, BluetoothProbe, SmsProbe, ActivityProbe, 
#         HardwareInfoProbe, RunningApplicationsProbe, LocationProbe, AppUsageProbe

def probeForTimeRange(probe, internalDataStore, start, end, includeBlanks = False, includeSelfAssessed = False):
    probeEntries = internalDataStore.getData(probe, start, end)
    if probeEntries is not None and (includeBlanks or probeEntries.count() > 0):
	    tempData = {}
	    for data in probeEntries:
		tempData = data["value"] 
	    #print tempData
	    

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


def aggregateForUser(probe, internalDataStore, answerKey, timeRanges, aggregator, includeBlanks = False):
    aggregates = []

    for (start, end) in timeRanges:
	if "Activity" in probe:
            data = aggregator(internalDataStore, start, end)
	else:
	    data = aggregator(probe, internalDataStore, start, end)
        if data is not None:
	    if "Activity" in probe:
                aggregates.append(aggregator(internalDataStore, start, end, includeBlanks))
	    else:
                aggregates.append(aggregator(probe, internalDataStore, start, end, includeBlanks))

    if answerKey is not None:
        internalDataStore.saveAnswer(answerKey, aggregates)

    return aggregates

@task()
def recentProbeDataScores(uuid):
    profile = Profile.objects.get(uuid = uuid)
    startTime = socialhealth_tasks.getStartTime(6, True)
    currentTime = time.time()
    timeRanges = [(start, start + 3600*4) for start in range(int(startTime), int(currentTime), 3600*4)]

    probeAnswerKeys = {'recentActivityProbeByHour': 'ActivityProbe', 'recentSmsProbeByHour': 'SmsProbe', 'recentCallLogProbeByHour': 'CallLogProbe', 
                       'recentBluetoothProbeByHour': 'BluetoothProbe', 'recentWifiProbeByHour': 'WifiProbe', 'recentSimpleLocationProbeByHour': 'LocationProbe', 
                       'recentRunningApplicationsProbeByHour': 'RunningApplicationsProbe', 'recentHardwareInfoProbeByHour': 'HardwareInfoProbe', 
                       'recentAppUsageProbeByHour': 'AppUsageProbe'}

    print profile
    token = socialhealth_tasks.getToken(profile, "app-uuid")
    internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)

    for probeAnswerKey, probe in probeAnswerKeys.iteritems():
        print probe
	if "Activity" in probe:
	    probeLevels = aggregateForUser(probe, internalDataStore, probeAnswerKey, timeRanges, activityForTimeRange, False)
	    print probeLevels
	else:
	    probeLevels = aggregateForUser(probe, internalDataStore, probeAnswerKey, timeRanges, probeForTimeRange, False)
