from celery import task
from openpds.core.models import Profile, Notification, Device
from bson import ObjectId
from pymongo import Connection
from django.conf import settings
import time
from datetime import date, timedelta
import json
import pdb
from gcm import GCM
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
import sqlite3
import random
from openpds.questions.socialhealth_tasks import getStartTime
from openpds import getInternalDataStore

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

@task()
def ensureFunfIndexes():
    profiles = Profile.objects.all()

    for profile in profiles:
        dbName = profile.getDBName()
        collection = connection[dbName]["funf"]
        collection.ensure_index([("time", -1), ("key", 1)], cache_for=7200, background=True, unique=True, dropDups=True)

@task()
def deleteUnusedProfiles():
    profiles = Profile.objects.all()
    start = getStartTime(60, False)

    for profile in profiles:
        dbName = profile.getDBName()
        collection = connection[dbName]["funf"]
        
        if collection.find({"time": { "$gte": start}}).count() == 0:
            connection.drop_database(dbName)
            profile.delete()

@task()
def recentProbeCounts():
    profiles = Profile.objects.all()
    startTime = getStartTime(1, False)
    
    for profile in profiles:
        ids = getInternalDataStore(profile, "", "Living Lab", "")
        probes = ["ActivityProbe", "SimpleLocationProbe", "CallLogProbe", "SmsProbe", "WifiProbe", "BluetoothProbe"]
        answer = {}
        for probe in probes:
            data = ids.getData(probe, startTime, None)
            answer[probe] = data.count()
        ids.saveAnswer("RecentProbeCounts", answer)

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
        gcm = GCM(settings.GCM_API_KEY)

        for device in Device.objects.filter(datastore_owner = profile):
            try:
                gcm.plaintext_request(registration_id=device.gcm_reg_id, data= {"action":"notify"})
            except Exception as e:
                print "Issue with sending notification to: %s, %s" % (profile.id, profile.uuid)
                print e

def notifyAll():
    for profile in Profile.objects.all():
        if Device.objects.filter(datastore_owner = profile).count() > 0:
            gcm = GCM(settings.GCM_API_KEY)
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
def sendVerificationSurvey():
    broadcastNotification(2, "Social Health Survey", "Please take a moment to complete this social health survey", "/survey/?survey=8")

@task()
def sendPast3DaysSurvey():
    broadcastNotification(2, "Social Health Survey", "Please take a moment to complete this social health survey", "/survey/?survey=5")

@task()
def sendExperienceSampleSurvey():
    broadcastNotification(2, "Social Health Survey", "Please take a moment to complete this social health survey", "/survey/?survey=9")

@task()
def sendSleepStartSurvey():
    broadcastNotification(2, "Sleep Tracker", "Please take this survey right before bed", "/survey/?survey=10")

@task()
def sendSleepEndSurvey():
    broadcastNotification(2, "Sleep Tracker", "Please take this survey right after waking up", "/survey/?survey=11")

def minDiff(elements, item):
    return min([abs(el - item) for el in elements])

@task()
def scheduleExperienceSamplesForToday():
    # We're scheduling 4 surveys / day, starting in the morning, with at least an hour of time in between each
    # assuming we send the first within 2 hours of running this, and need to get all surveys done within 8 hours,
    # we can build the list of delays via simple rejection  
    maxDelay = 3600 * 8
    delays = [random.randint(0,maxDelay)]
    while len(delays) < 4:
        nextDelay = random.randint(0, maxDelay)
        if minDiff(delays, nextDelay) >= 3600:
            delays.append(nextDelay)
    print delays
    print [time.strftime("%H:%M", time.localtime(1385042444 + d)) for d in delays]
    for t in delays:
        print "sending survey with %s second delay..." % str(t)
        sendExperienceSampleSurvey.apply_async(countdown = t)

@task() 
def findMusicGenres():
    profiles = Profile.objects.all()
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    artistQuery = "PREFIX dbpprop: <http://dbpedia.org/property/> PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> select ?artist ?genre from <http://dbpedia.org> where { ?artist rdfs:label \"%s\"@en . ?artist dbpprop:genre ?genre }" 
    albumQuery = "PREFIX dbpedia-owl: <http://dbpedia.org/ontology/> PREFIX dbpprop: <http://dbpedia.org/property/> select ?album ?genre from  <http://dbpedia.org> where { ?album a dbpedia-owl:Album . ?album dbpprop:name '%s'@en . ?album dbpprop:genre ?genre }"

    for profile in profiles:
        dbName = profile.getDBName()
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
    outputConnection = sqlite3.connect("openpds/static/dump.db")
    c = outputConnection.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS funf (user_id integer, key text, time real, value text, PRIMARY KEY (user_id, key, time) on conflict ignore)")
    startTime = getStartTime(3, False)#max(1378008000, startTimeRow[0]) if startTimeRow is not None else 1378008000
    for profile in profiles:
        dbName = profile.getDBName()
        funf = connection[dbName]["funf"]
        user = int(profile.id)
        c.executemany("INSERT INTO funf VALUES (?,?,?,?)", [(user,d["key"][d["key"].rfind(".")+1:],d["time"],"%s"%d["value"]) for d in funf.find({"time": {"$gte": startTime}}) if d["key"] is not None])

    outputConnection.commit()
    outputConnection.close()

@task()
def dumpSurveyData():
    profiles = Profile.objects.all()
    outputConnection = sqlite3.connect("openpds/static/dump.db")
    c = outputConnection.cursor()
    #c.execute("DROP TABLE IF EXISTS survey;")
    c.execute("CREATE TABLE IF NOT EXISTS survey (user_id integer, key text, time real, value text, PRIMARY KEY (user_id, key, time) on conflict ignore);")

    for profile in profiles:
        dbName = profile.getDBName()
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

