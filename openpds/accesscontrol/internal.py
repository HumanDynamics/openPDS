import ast
import sqlite3
import os
import stat
import threading
from openpds.core.models import Profile
from openpds.accesscontrol.models import Settings, Context
from openpds import settings
import datetime
import math

class AccessControlledInternalDataStore(object):
    def __init__(self, ids):
        self.ids = ids
        self.profile = ids.profile
        self.datastore_owner_id = self.profile.id
        self.app_id = ids.app_id
        self.lab_id = ids.lab_id
        self.mapping = {'ActivityProbe': 'activity_probe', 'SmsProbe': 'sms_probe', 'CallLogProbe': 'call_log_probe', 'BluetoothProbe':'bluetooth_probe', 'WifiProbe': 'wifi_probe', 'LocationProbe': 'simple_location_probe', 'ScreenProbe': 'screen_probe', 'RunningApplicationsProbe': 'running_applications_probe', 'HardwareInfoProbe': 'hardware_info_probe', 'AppUsageProbe': 'app_usage_probe'} 

    def saveAnswer(self, key, data):
        return self.ids.saveAnswer(key, data)

    def getAnswer(self, key):
        return self.ids.getAnswer(key)

    def getAnswerList(self, key):
        return self.ids.getAnswerList(key)

    def saveData(self, data, collectionname):
        return self.ids.saveData(data, collectionname)

    def testServiceEnabled(self):
        result = False
        settingsObjects = Settings.objects.filter(datastore_owner_id=self.datastore_owner_id, app_id=self.app_id, lab_id=self.lab_id, service_id=self.service_id)
        # NOTE: The below is a hack to assure that things still function for those on a field trial where opt-in is implied (thus don't have settings entries)
        if len(settingsObjects) == 0:
            result = True
        return result

    def getData(self, probe, startTime, endTime):
        dataLocations = None
        if probe == "LocationProbe":
            dataLocations = set()
            cursor = self.ids.getData(probe, startTime, endTime)
            if cursor:
                for entry in cursor:
                    dataLocations.add((entry[u'value'][u'mlatitude'], entry[u'value'][u'mlongitude']))

        column = self.mapping[probe]
        probe_flag = False
        try:
            settingsObject = Settings.objects.get(datastore_owner_id=self.datastore_owner_id, app_id=self.app_id, lab_id=self.lab_id)
            try:
                contextObject = Context.objects.get(pk=settingsObject.context_label_id)
            except Context.DoesNotExist:
                contextObject = None
        except Settings.DoesNotExist:
            settingsObject = None
            contextObject = None

        # NOTE: Hack for those who don't have settings entries (field trial users). This will go away in the long term
        if settingsObject is None:
            probe_flag = True
            validTimes = True
            validLocations = True
        else:
            probe_flag = settingsObject.__dict__[column]
            if startTime is None or endTime is None:
                validTimes = False
                validLocations = False
            else:
                validTimes = self.checkTime(startTime, endTime, contextObject)
                #print "validTimes; %s"%validTimes
                validLocations = self.checkLocation(startTime, endTime, contextObject, dataLocations)
        
        if probe_flag and validTimes and validLocations:
            return self.ids.getData(probe, startTime, endTime)
        else:
            #print probe_flag, validTimes, validLocations
            return None

    def checkTime(self, startTime, endTime, context):

        timestamp_start = datetime.datetime.fromtimestamp(startTime)
        #print timestamp_start.strftime('%Y-%m-%d %H:%M')
        start_hour = int(timestamp_start.strftime('%H'))
        start_minute = int(timestamp_start.strftime('%M'))
        start_time = datetime.datetime.now().replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        start_day = timestamp_start.weekday()
        timestamp_end = datetime.datetime.fromtimestamp(endTime)
        end_hour = int(timestamp_end.strftime('%H'))
        end_minute = int(timestamp_end.strftime('%M'))
        end_time = datetime.datetime.now().replace(hour=end_hour, minute=end_minute, second=0, microsecond=0)
        end_day = timestamp_end.weekday()

        timeFlag = False
        dayFlag = True

        context_start = [int(start.strip()) for start in context.context_duration_start.split(':')]
        context_start_hour = context_start[0]
        context_start_minute = context_start[1]
        context_start_time = datetime.datetime.now().replace(hour=context_start_hour, minute=context_start_minute, second=0, microsecond=0)

        context_end = [int(end.strip()) for end in context.context_duration_end.split(':')]
        context_end_hour = context_end[0]
        context_end_minute = context_end[1]
        context_end_time = datetime.datetime.now().replace(hour=context_end_hour, minute=context_end_minute, second=0, microsecond=0)


        if context_start_time <= start_time and end_time <= context_end_time:
            timeFlag = True

        #Python datetime: Monday = 0, Sunday = 6
        #Client code will be fixed to reflect this day ordering
        context_days = context.context_duration_days
        context_days_list = [int(x) for x in context_days[1:-1].split(',')]
        if start_day < end_day:
            start_day_temp = start_day
            while start_day_temp <= end_day:
                if context_days_list[start_day_temp] != 1:
                    dayFlag = False
                    break
                start_day_temp += 1
        elif start_day > end_day:
            start_day_temp = start_day
            while start_day_temp <= 6:
                if context_days_list[start_day_temp] != 1:
                    dayFlag = False
                    break
                start_day_temp += 1
            end_day_temp = 0
            while end_day_temp <= end_day:
                if context_days_list[end_day_temp] != 1:
                    dayFlag = False
                    break
                end_day_temp += 1
        else:
            if context_days_list[start_day] != 1:
                dayFlag = False
        #print "dayFlag, timeFlag: %s, %s"%(dayFlag, timeFlag)
        return dayFlag and timeFlag

    def checkLocation(self, startTime, endTime, context, dataLocations):
        if dataLocations is None:
            dataLocations = set()
            cursor = self.ids.getData("LocationProbe", startTime, endTime)
            if cursor:
                for entry in cursor:
                    dataLocations.add((entry[u'value'][u'mlatitude'], entry[u'value'][u'mlongitude']))

        contextLocations = set()
        temp_places = [x.strip() for x in context.context_places[1:-1].split("lat/lng:") if x]        

        #No location specified in the context, alright to use the data.
        if len(temp_places) == 0:
            return True

        contextLocations = []
        for place in temp_places:
            if '),' in place:
                placeValues = [float(x.strip()) for x in place[:-1][1:-1].split(',')]
            else:
                placeValues = [float(x.strip()) for x in place[1:-1].split(',')]
            contextLocations.append((placeValues[0], placeValues[1]))
        
        dataLocationsChecks = [0] * len(dataLocations)
        dataLocationsIndex = 0

        #Haversine distance computation.
        #Source: http://rosettacode.org/wiki/Haversine_formula#Python
        R = 6372.8 # Earth radius in kilometers
        for dataLocation in dataLocations:
            for contextLocation in contextLocations:
                dLat = math.radians(dataLocation[0] - contextLocation[0])
                dLon = math.radians(dataLocation[1] - contextLocation[1])
                lat1 = math.radians(contextLocation[0])
                lat2 = math.radians(dataLocation[0])
        
                a = math.sin(dLat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dLon/2)**2
                c = 2*math.asin(math.sqrt(a))

                distance = R * c * 1000
                if distance < 500:
                    dataLocationsChecks[dataLocationsIndex] = 1
                    break
            dataLocationsIndex += 1

        if all(check == 1 for check in dataLocationsChecks):
            return True        
        else:
            return False


def getAccessControlledInternalDataStore(ids):
    try:
        internalDataStore = AccessControlledInternalDataStore(ids)
    except Exception as e:
        internalDataStore = None
        print str(e)
    return internalDataStore

