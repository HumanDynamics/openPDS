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
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
import sqlite3

"""the MONGODB_DATABASE_MULTIPDS setting is set by extract-user-middleware in cases where we need multiple PDS instances within one PDS service """


connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

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
        dbName = profile.getDBName()
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
        dbName = profile.getDBName() 
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
        dbName = profile.getDBName()
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
        dbName = profile.getDBName()
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

