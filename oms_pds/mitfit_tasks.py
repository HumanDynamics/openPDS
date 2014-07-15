from __future__ import division
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
from collections import Counter
import sqlite3
import socialhealth_tasks
import places_tasks
import sys
import bisect
from operator import itemgetter, attrgetter

class LeaderboardRanking():
    def __init__(self, user_entry):
        self.average_activity_rate = user_entry["average_activity_rate"]
        self.max_high_activity_rate = user_entry["max_high_activity_rate"]       
        self.min_low_activity_rate = user_entry["min_low_activity_rate"]
 
    def get_average_activity_rate(self):
	return self.average_activity_rate

    def get_max_high_activity_rate(self):
	return self.max_high_activity_rate

    def get_min_low_activity_rate(self):
	return self.min_low_activity_rate

def calculatePercentile(orderedList, number):
    position = orderedList.index(number)
    percentile = (position + 0.5)/len(orderedList)
    return round(percentile*100)

def leaderboardComputation(internalDataStore):
    #probeEntries = internalDataStore.getData( probe, start, end)
    answer = internalDataStore.getAnswerList("recentActivityProbeByHour")
    answer = answer[0]["value"] #if answer.count() > 0 else []
    num_answers = len(answer)
    #print answer[0]["value"]
    activity_rate = 0
    average_activity_rate = 0
    max_high_activity_rate = sys.float_info.min
    min_low_activity_rate = sys.float_info.max
    for activityAnswer in answer:
	#print activityAnswer
        high_activity_rate = activityAnswer["high"]/activityAnswer["total"]
        low_activity_rate = activityAnswer["low"]/activityAnswer["total"]
        activity_rate = activity_rate + ((0.7*high_activity_rate) + (0.3*low_activity_rate))
        #print "activity_rate: " + str(activity_rate) + ", high_activity_rate: " + str(high_activity_rate) + ", low_activity_rate: " + str(low_activity_rate)  
        if high_activity_rate > max_high_activity_rate:
            max_high_activity_rate = high_activity_rate
        if low_activity_rate < min_low_activity_rate:
	    min_low_activity_rate = low_activity_rate 
    if len(answer) > 0:
        average_activity_rate = activity_rate/len(answer)
    user_activity = { "average_activity_rate": average_activity_rate, "max_high_activity_rate": max_high_activity_rate, "min_low_activity_rate": min_low_activity_rate}
    return user_activity

def aggregateLeaderboardComputation(internalDataStore, answerKey, aggregator, includeBlanks = False):
    aggregates = []

    data = aggregator(internalDataStore)
    if data is not None:
        aggregates.append(data)

    #if answerKey is not None:
    #    internalDataStore.saveAnswer(answerKey, aggregates)
    return aggregates

@task()
def leaderboardComputationTask():
    profiles = Profile.objects.all()
#    profiles = []
#    profiles.append(Profile.objects.get(uuid="341cc5cd-0f42-45f1-9f66-273ac3ed8b2e"))

    unsorted_dict = {}
    for profile in profiles:
	token = socialhealth_tasks.getToken(profile, "app-uuid")
	internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)
	
	values = aggregateLeaderboardComputation(internalDataStore, "activityStats", leaderboardComputation, False)
        unsorted_dict[profile.uuid] = LeaderboardRanking({ "average_activity_rate": values[0]["average_activity_rate"], "max_high_activity_rate": values[0]["max_high_activity_rate"], "min_low_activity_rate": values[0]["min_low_activity_rate"]})
	
    #sorted_dict = sorted(unsorted_dict.values(), key=attrgetter('average_activity_rate'))
    sorted_dict = sorted(unsorted_dict, key = lambda uuid: unsorted_dict[uuid].average_activity_rate, reverse=False)
 
    average_activity_rates_list = []
    for uuid in sorted_dict:
	average_activity_rates_list.append(unsorted_dict[uuid].get_average_activity_rate())
   
    for uuid in sorted_dict:
        profile = Profile.objects.get(uuid=uuid)
        token = socialhealth_tasks.getToken(profile, "app-uuid")
        internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)

	percentileValue = calculatePercentile(average_activity_rates_list, unsorted_dict[uuid].get_average_activity_rate())	

        user_activity_list = []
        user_activity_dict = { "average_activity_rate": unsorted_dict[uuid].get_average_activity_rate(), "max_high_activity_rate": unsorted_dict[uuid].get_max_high_activity_rate(), "min_low_activity_rate": unsorted_dict[uuid].get_min_low_activity_rate(), "rank": {"own": len(sorted_dict) - sorted_dict.index(uuid), "total": len(sorted_dict), "percentile": percentileValue} }
        user_activity_list.append(user_activity_dict)
        internalDataStore.saveAnswer("activityStats", user_activity_list)


###################
# Active Locations #
###################

def activeLocationsComputation(internalDataStore):
    activityAnswerList = internalDataStore.getAnswerList("recentActivityProbeByHour")
    activityAnswerList = activityAnswerList[0]["value"] if activityAnswerList.count() > 0 else []
    locationPoints = []
    for activityAnswer in activityAnswerList:
        activity_rate = (500*(activityAnswer["high"] + activityAnswer["low"]))/activityAnswer["total"]
        start_time = activityAnswer["start"]
	end_time = activityAnswer["end"]
	#print activity_rate
	if activity_rate > 1:
	    locationAnswerList = internalDataStore.getAnswerList("recentSimpleLocationProbeByHour")
	    locationAnswerList = locationAnswerList[0]["value"] if locationAnswerList.count() > 0 else []
	    for locationAnswer in locationAnswerList:
		#print locationAnswer
		if start_time == locationAnswer["start"] and end_time == locationAnswer["end"]:
		    #print locationAnswer["centroid"]
		    if locationAnswer["centroid"]:
		        locationPoints.append(locationAnswer["centroid"][0])

    return locationPoints

#    return user_activity

@task()
def findActiveLocationsTask():
    profiles = Profile.objects.all()

    location_frequencies = {}
    for profile in profiles:
        token = socialhealth_tasks.getToken(profile, "app-uuid")
        internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)

        values = activeLocationsComputation(internalDataStore)
	print profile.uuid
	print values
	
	for value in values:
		location_value = tuple((round(value[0],4), round(value[1],4)))
		if location_value in location_frequencies:
			location_frequencies[location_value] = location_frequencies[location_value] + 1
		else:
			location_frequencies[location_value] = 1

    print location_frequencies

    location_frequencies_list = []
    for key  in location_frequencies:
	print key 
	location_value = { "lat": key[0], "lng": key[1], "count": location_frequencies[key]}	
	location_frequencies_list.append(location_value)

    print location_frequencies_list

    for profile in profiles:
        token = socialhealth_tasks.getToken(profile, "app-uuid")
        internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)
	
	internalDataStore.saveAnswer("activeLocations", location_frequencies_list)	
