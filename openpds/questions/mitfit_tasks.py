from __future__ import division
from celery import task
from openpds.core.models import Profile, Notification, Device
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
from openpds.core.models import Profile
from openpds.backends.mongo import getInternalDataStore
from collections import Counter
import sqlite3
import socialhealth_tasks
import places_tasks
import sys
import bisect
from operator import itemgetter, attrgetter
import datetime
import random
from openpds.accesscontrol.models import Optin

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
	if activityAnswer["total"] > 0:
            high_activity_rate = activityAnswer["high"]/activityAnswer["total"]
            low_activity_rate = activityAnswer["low"]/activityAnswer["total"]
	else:
	    high_activity_rate = 0 
            low_activity_rate = 0
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
#	token = socialhealth_tasks.getToken(profile, "app-uuid")
#	internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)

	internalDataStore = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")
	
	values = aggregateLeaderboardComputation(internalDataStore, "activityStats", leaderboardComputation, False)
        unsorted_dict[profile.uuid] = LeaderboardRanking({ "average_activity_rate": values[0]["average_activity_rate"], "max_high_activity_rate": values[0]["max_high_activity_rate"], "min_low_activity_rate": values[0]["min_low_activity_rate"]})
	
    #sorted_dict = sorted(unsorted_dict.values(), key=attrgetter('average_activity_rate'))
    sorted_dict = sorted(unsorted_dict, key = lambda uuid: unsorted_dict[uuid].average_activity_rate, reverse=False)
 
    average_activity_rates_list = []
    for uuid in sorted_dict:
	average_activity_rates_list.append(unsorted_dict[uuid].get_average_activity_rate())
   
    for uuid in sorted_dict:
        profile = Profile.objects.get(uuid=uuid)
#        token = socialhealth_tasks.getToken(profile, "app-uuid")
#        internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)

	internalDataStore = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")

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
        start_time = activityAnswer["start"]
	end_time = activityAnswer["end"]
	if activityAnswer["high"] > 0:
	    locationAnswerList = internalDataStore.getAnswerList("recentSimpleLocationProbeByHour")
	    locationAnswerList = locationAnswerList[0]["value"] if locationAnswerList.count() > 0 else []
	    for locationAnswer in locationAnswerList:
		if start_time == locationAnswer["start"] and end_time == locationAnswer["end"]:
		    if locationAnswer["centroid"]:
		        locationPoints.append(locationAnswer["centroid"][0])

    return locationPoints

@task()
def findActiveLocationsTask():
    profiles = Profile.objects.all()

    location_frequencies = {}
    for profile in profiles:

        try:
            optin_object = Optin.objects.get(datastore_owner = profile, app_id = "Living Lab", lab_id = "MIT-FIT")
        except Optin.DoesNotExist:
            optin_object = None

	if optin_object:
	    if optin_object.data_aggregation == 0:
		continue
	
	#print profile.id

	internalDataStore = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")
        values = activeLocationsComputation(internalDataStore)
	for value in values:
		location_value = tuple((round(value[0],4), round(value[1],4)))
		if location_value in location_frequencies:
			location_frequencies[location_value] = location_frequencies[location_value] + 1
		else:
			location_frequencies[location_value] = 1

    location_frequencies_list = []
    for key  in location_frequencies:
	location_value = { "lat": key[0], "lng": key[1], "count": location_frequencies[key]}	
	location_frequencies_list.append(location_value)

    for profile in profiles:
	internalDataStore = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")
	internalDataStore.saveAnswer("activeLocations", location_frequencies_list)	


###################
# Active Times #
###################

def activeTimesComputation(internalDataStore):
    activityAnswerList = internalDataStore.getAnswerList("recentActivityProbeByHour")
    activityAnswerList = activityAnswerList[0]["value"] if activityAnswerList.count() > 0 else []
    time_counts = [0] * 24
    for activityAnswer in activityAnswerList:
#        activity_rate = (500*(activityAnswer["high"] + activityAnswer["low"]))/activityAnswer["total"]
        start_time = activityAnswer["start"]
        end_time = activityAnswer["end"]
        #print activity_rate
#        if activity_rate > 1:
	if activityAnswer["high"] > 0:
	    start_hours = datetime.datetime.fromtimestamp(start_time).hour
	    time_counts[start_hours] += 1

    return time_counts

@task()
def findActiveTimesTask():
    profiles = Profile.objects.all()

    time_averages = [0] * 24
    num_users = 0
    
    for profile in profiles:
	num_users += 1
#        token = socialhealth_tasks.getToken(profile, "app-uuid")
#        internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)

	internalDataStore = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")

        user_time_averages = activeTimesComputation(internalDataStore)

        for i in range(len(time_averages)):
	    time_averages[i] += user_time_averages[i]

    #print num_users
    #print time_averages 
    for i in range(len(time_averages)):
	time_averages[i] = time_averages[i] // num_users

    for profile in profiles:
#        token = socialhealth_tasks.getToken(profile, "app-uuid")
#        internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)

	internalDataStore = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")

        internalDataStore.saveAnswer("activeTimes", time_averages)


###########################
# Testing Recommendations #
###########################

data = [
{'name': 'Running 101', 'type': 'running', 'id': 1},
{'name': 'Running 102', 'type': 'running', 'id': 2},
{'name': 'Learn to love running', 'type': 'running', 'id': 3},
{'name': 'Running Intermediate', 'type': 'running', 'id': 4},
{'name': 'Running Advanced', 'type': 'running', 'id': 5},
{'name': 'Squash 101', 'type': 'squash', 'id': 6},
{'name': 'Squash 102', 'type': 'squash', 'id': 7},
{'name': 'Learn to love squash', 'type': 'squash', 'id': 8},
{'name': 'Squash Intermediate', 'type': 'squash', 'id': 9},
{'name': 'Squash Advanced', 'type': 'squash', 'id': 10},
{'name': 'Swimming 101', 'type': 'swimming', 'id': 11},
{'name': 'Swimming 102', 'type': 'swimming', 'id': 12},
{'name': 'Learn to love swimming', 'type': 'swimming', 'id': 13},
{'name': 'Swimming Intermediate', 'type': 'swimming', 'id': 14},
{'name': 'Swimming Advanced', 'type': 'swimming', 'id': 15},
{'name': 'Bootcamp Fitness 101', 'type': 'bootcamp-fitness', 'id': 16},
{'name': 'Bootcamp Fitness 102', 'type': 'bootcamp-fitness', 'id': 17},
{'name': 'Learn to love bootcamp fitness', 'type': 'bootcamp-fitness', 'id': 18},
{'name': 'Bootcamp Fitness Intermediate', 'type': 'bootcamp-fitness', 'id': 19},
{'name': 'Bootcamp Fitness Advanced', 'type': 'bootcamp-fitness', 'id': 20},
{'name': 'Tennis 101', 'type': 'tennis', 'id': 21},
{'name': 'Tennis 102', 'type': 'tennis', 'id': 22},
{'name': 'Learn to love tennis', 'type': 'tennis', 'id': 23},
{'name': 'Tennis Intermediate', 'type': 'tennis', 'id': 24},
{'name': 'Tennis Advanced', 'type': 'tennis', 'id': 25}
]


def populateEventsForUsers():
    profiles = Profile.objects.all()
    for profile in profiles:
#        token = socialhealth_tasks.getToken(profile, "app-uuid")
#        internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)

	internalDataStore = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")

	events = []
        random_numbers = random.sample(range(25), 7)
        for random_number in random_numbers:
            events.append(data[random_number])
        #print events
        internalDataStore.saveAnswer("mitfitEventRegistrations", events)


def eventRecommendationComputation(internalDataStore, eventRegistrations, profile):
    eventRegistrationAnswerList = internalDataStore.getAnswerList("mitfitEventRegistrations")
    eventRegistrationAnswerList = eventRegistrationAnswerList[0]["value"] if eventRegistrationAnswerList.count() > 0 else []
    userEventRegistrations = set()
    for eventRegistrationAnswer in eventRegistrationAnswerList:
	#print eventRegistrationAnswer[u'id']
	eventRegistrationAnswerFrozenset = frozenset(eventRegistrationAnswer.items())
	#print eventRegistrationAnswerFrozenset
	userEventRegistrations.add(eventRegistrationAnswerFrozenset)
	if eventRegistrationAnswerFrozenset in eventRegistrations.keys():
	    eventRegistrations[eventRegistrationAnswerFrozenset].append(profile)
	else:
	    tempEventRegistrations = []
	    tempEventRegistrations.append(profile)
	    eventRegistrations[eventRegistrationAnswerFrozenset] = tempEventRegistrations
	#print eventRegistrations
    return eventRegistrations, userEventRegistrations

@task()
def recommendEvents():
    profiles = Profile.objects.all()
    eventRegistrations = {}
    userRegistrations = {}
    for profile in profiles:
	#print profile.uuid
#        token = socialhealth_tasks.getToken(profile, "app-uuid")
#        internalDataStore = socialhealth_tasks.getInternalDataStore(profile, "Living Lab", "Social Health Tracker", token)

	internalDataStore = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")

        eventRegistrations, userEventRegistrations = eventRecommendationComputation(internalDataStore, eventRegistrations, profile.uuid)
	userRegistrations[profile.uuid] = userEventRegistrations
    #print eventRegistrations
   
    eventSet = set()
    jaccardCoefficientDict = {}
    for event1 in eventRegistrations.keys():
	for event2 in eventRegistrations.keys():
	    if event1 != event2:
		usersEvent1 = eventRegistrations[event1]
		usersEvent2 = eventRegistrations[event2]
		intersectUsers = list(set(usersEvent1) & set(usersEvent2))
		unionUsers = list(set(usersEvent1) | set(usersEvent2))
		jaccardCoefficientKey = (event1, event2)
		eventSet.add(event1)
		eventSet.add(event2)
		if len(unionUsers) > 0:
		    jaccardCoefficientDict[jaccardCoefficientKey] = len(intersectUsers)/len(unionUsers)
		else:
		    jaccardCoefficientDict[jaccardCoefficientKey] = 0
    #print jaccardCoefficientDict

    for profile in profiles:
        #print profile.uuid
	recommendedEvents = {}
	for userRegisteredEvent in userRegistrations[profile.uuid]:
	    for event in eventSet:
		if userRegisteredEvent != event:
			if event in recommendedEvents:
			    if jaccardCoefficientDict[(userRegisteredEvent, event)] > recommendedEvents[event]:
			        recommendedEvents[event] = jaccardCoefficientDict[(userRegisteredEvent, event)]
			else:
			    recommendedEvents[event] = jaccardCoefficientDict[(userRegisteredEvent, event)]
        #print recommendedEvents
	sortedRecommendedEvents = sorted(recommendedEvents.items(), key = lambda recommendedEvent: recommendedEvent[1], reverse=True)
	#print sortedRecommendedEvents

#	for event in sortedRecommendedEvents[:3]:
#	    for eventDetails in event[0]:
#		if u'name' in eventDetails[0]:
#	            print eventDetails[1] + ", " ,
#	print 

def testGetData():
    profiles = Profile.objects.all()
    #print profiles[17].uuid
#    token = socialhealth_tasks.getToken(profiles[17], "app-uuid")
#    internalDataStore = socialhealth_tasks.getInternalDataStore(profiles[17], "Living Lab", "Social Health Tracker", token)

    internalDataStore = getInternalDataStore(profile, "Living Lab", "MIT-FIT", "")

    probes = ["LocationProbe", "ActivityProbe", "SmsProbe", "CallLogProbe", "BluetoothProbe", "WifiProbe", "ScreenProbe"]
    startTime = 1403136000
    endTime = 1403222400
    internalDataStore.getData(probes[1], startTime, endTime)
