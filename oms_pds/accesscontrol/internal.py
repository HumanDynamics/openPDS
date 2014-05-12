import ast
import sqlite3
import os
import stat
import threading
from pymongo import Connection
from oms_pds.pds.models import Profile
from oms_pds.accesscontrol.models import Settings
from oms_pds import settings

class AccessControlledInternalDataStore(object):
    def __init__(self, profile, app_id, lab_id):
        self.profile = profile
        self.datastore_owner_id = self.profile.id
        self.app_id = app_id
        self.lab_id = lab_id
#        self.service_id = service_id
#        self.enabled = self.testServiceEnabled()
        self.mapping = {'ActivityProbe': 'activity_probe', 'SmsProbe': 'sms_probe', 'CallLogProbe': 'call_log_probe', 'BluetoothProbe':'bluetooth_probe', 'WifiProbe': 'wifi_probe', 'LocationProbe': 'simple_location_probe', 'ScreenProbe': 'screen_probe', 'RunningApplicationsProbe': 'running_applications_probe', 'HardwareInfoProbe': 'hardware_info_probe', 'AppUsageProbe': 'app_usage_probe'} 

#        print "service enabled? ", self.enabled

    def testServiceEnabled(self):
        result = False
        settingsObjects = Settings.objects.filter(datastore_owner_id=self.datastore_owner_id, app_id=self.app_id, lab_id=self.lab_id, service_id=self.service_id)
        # NOTE: The below is a hack to assure that things still function for those on a field trial where opt-in is implied (thus don't have settings entries)
        if len(settingsObjects) == 0:
            result = True
#        for settings in settingsObjects:
#            if settings.enabled:
#                result = True
        return result

    def getData(self, probe, startTime, endTime):
#        if not self.enabled:
#            print "Service not enabled"
#            return None
#        else:
         column = self.mapping[probe]
         probe_flag = False
         settingsObjects = Settings.objects.filter(datastore_owner_id=self.datastore_owner_id, app_id=self.app_id, lab_id=self.lab_id)
         # NOTE: Hack for those who don't have settings entries (field trial users). This will go away in the long term
         if len(settingsObjects) == 0:
            probe_flag = True
         for settings in settingsObjects:
            #print settings.__dict__
            probe_flag = settings.__dict__[column]
	 #print probe_flag
         if probe_flag:
            return self.getDataInternal(probe, startTime, endTime)
         else:
            return None

    def getDataInternal(self, probe, startTime, endTime):
        return True

def getAccessControlledInternalDataStore(profile, app_id, lab_id):
    try:
        internalDataStore = AccessControlledInternalDataStore(profile, app_id, lab_id)
    except Exception as e:
        internalDataStore = None
        print str(e)
    return internalDataStore

