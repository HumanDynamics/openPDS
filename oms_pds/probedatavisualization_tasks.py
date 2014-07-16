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
import places_tasks

# probes: CallLogProbe, WifiProbe, BluetoothProbe, SmsProbe, ActivityProbe, 
#         HardwareInfoProbe, RunningApplicationsProbe, LocationProbe, AppUsageProbe

def probeForTimeRange(probe, internalDataStore, start, end, includeBlanks = False, includeSelfAssessed = False):
    probeEntries = internalDataStore.getData(probe, start, end)
    if probeEntries is not None and (includeBlanks or probeEntries.count() > 0):
	values = [data["value"] for data in probeEntries]
	#print values
        if probe == 'LocationProbe':
	    #Commented out next line because locations obtained through wifi have maccuracy > 30.
#	    values = [value for value in values if float(value["maccuracy"]) < 30]
	    clusters = places_tasks.clusterFunfLocations(values, 20)
	    #We're only interested in places that have more than 3 samples - either the users stayed there a while, or returned there a number of times)
            clusters = [cluster for cluster in clusters if len(cluster) > 3]
            centroids = [places_tasks.centroid(cluster) for cluster in clusters]
	    
            location = { "start": start, "end": end, "centroid": centroids }
	    return location
	elif probe == "ActivityProbe":
	    lowActivityIntervals = highActivityIntervals = totalIntervals = 0
	    for value in values:
                if ("total_intervals" in value):
                    totalIntervals += value["total_intervals"]
                    lowActivityIntervals += value["low_activity_intervals"]
                    highActivityIntervals += value["high_activity_intervals"]
                else:
                    totalIntervals += 1
                    lowActivityIntervals += 1 if value["activitylevel"] == "low" else 0
                    highActivityIntervals += 1 if value["activitylevel"] == "high" else 0

            activity = { "start": start, "end": end, "total": totalIntervals, "low": lowActivityIntervals, "high": highActivityIntervals }
            return activity
    return None
	    

def aggregateForUser(probe, internalDataStore, answerKey, timeRanges, aggregator, includeBlanks = False):
    aggregates = []

    for (start, end) in timeRanges:
	data = aggregator(probe, internalDataStore, start, end)
        if data is not None:
            aggregates.append(aggregator(probe, internalDataStore, start, end, includeBlanks))

    if answerKey is not None:
        internalDataStore.saveAnswer(answerKey, aggregates)

    return aggregates

@task()
def recentProbeDataScores():
    profiles = Profile.objects.all()
    for profile in profiles:
        startTime = socialhealth_tasks.getStartTime(6, True)
        currentTime = time.time()
        timeRanges = [(start, start + 3600) for start in range(int(startTime), int(currentTime), 3600)]

        probeAnswerKeys = {'recentActivityProbeByHour': 'ActivityProbe', 'recentSmsProbeByHour': 'SmsProbe', 'recentCallLogProbeByHour': 'CallLogProbe', 
                       'recentBluetoothProbeByHour': 'BluetoothProbe', 'recentWifiProbeByHour': 'WifiProbe', 'recentSimpleLocationProbeByHour': 'LocationProbe', 
                       'recentRunningApplicationsProbeByHour': 'RunningApplicationsProbe', 'recentHardwareInfoProbeByHour': 'HardwareInfoProbe', 
                       'recentAppUsageProbeByHour': 'AppUsageProbe'}

#        print profile
#        token = socialhealth_tasks.getToken(profile, "app-uuid")
#        internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)
        internalDataStore = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")

	#for testing, currently use the following user
	#if profile.uuid == "341cc5cd-0f42-45f1-9f66-273ac3ed8b2e":

        for probeAnswerKey, probe in probeAnswerKeys.iteritems():
	    probeLevels = aggregateForUser(probe, internalDataStore, probeAnswerKey, timeRanges, probeForTimeRange, False)
