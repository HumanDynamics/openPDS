from celery import task
from openpds.core.models import Profile, Notification, Device
from bson import ObjectId
from pymongo import Connection
from django.conf import settings
import time
from datetime import date, timedelta
import datetime
import json
import pdb
import math
import cluster
from gcm import GCM
from openpds.core.models import Profile
from openpds import getInternalDataStore
from openpds.questions.socialhealth_tasks import getStartTime
#from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
import sqlite3

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

ANSWERKEY_NAME_MAPPING = {
    "gfsa": "My Team's Status"
}

probes = ["LocationProbe", "WifiProbe", "BluetoothProbe"]
probesPrettyNames = {"LocationProbe":"Last Location scan", "WifiProbe":"Last Wifi scan", "BluetoothProbe":"Last Bluetooth scan"}
def recentGfsaScore(ids):
	startTime = getStartTime(7, False)
	answer = {}
	for probe in probes:
	    probePrettyName=probesPrettyNames[probe]
	    try:
            	data = ids.getData(probe, startTime, None)
		dataList = [d["value"]["timestamp"] for d in data]
		dataList.sort()
		maxDate = dataList.pop()
		maxDateISO=datetime.datetime.fromtimestamp(maxDate)
            	answer[probePrettyName] = maxDateISO.strftime("%d %B %Y %I:%M%p")#onvert to string
	    except Exception, ex:
		#print "error: {}".format(ex)
           	answer[probePrettyName] = "None"
	#print answer
	ids.saveAnswer("recentGfsaScores", answer)
        pass

@task()
def recentGfsaScores():
        for profile in Profile.objects.all():
                ids = getInternalDataStore(profile, "Living Lab", "gfsa", "")
                recentGfsaScore(ids)

