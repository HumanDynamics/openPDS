#import pprint
#import pdb
import time
funfuniques = {
  "edu.mit.media.funf.probe.builtin.ActivityProbe": {
    "_id": {
      "$oid": "540a2b2491cfc86cda60813c"
    }, 
    "key": "edu.mit.media.funf.probe.builtin.ActivityProbe", 
    "time": 1409952534.912, 
    "value": {
      "high_activity_intervals": 0, 
      "low_activity_intervals": 0, 
      "timestamp": 1409952534.912, 
      "total_intervals": 14
    }
  }, 
  "edu.mit.media.funf.probe.builtin.BluetoothProbe": {
    "_id": {
      "$oid": "5408e7d991cfc86cda603ad6"
    }, 
    "key": "edu.mit.media.funf.probe.builtin.BluetoothProbe", 
    "time": 1409868872.866, 
    "value": {
      "android-bluetooth-device-extra-class": {
        "mclass": 7936
      }, 
      "android-bluetooth-device-extra-device": {
        "maddress": "2C:B4:3A:29:D5:3B"
      }, 
      "android-bluetooth-device-extra-rssi": -100, 
      "timestamp": 1409868872.866
    }
  }, 
  "edu.mit.media.funf.probe.builtin.CallLogProbe": {
    "_id": {
      "$oid": "5409f31b91cfc81dda364d0a"
    }, 
    "key": "edu.mit.media.funf.probe.builtin.CallLogProbe", 
    "time": 1409936189.572, 
    "value": {
      "_id": 1252, 
      "date": {
        "$numberLong": "1409936189572"
      }, 
      "duration": 0, 
      "number": "5188263335", 
      "numbertype": "{\"ONE_WAY_HASH\":\"b6589fc6ab0dc82cf12099d1c2d40ab994e8410c\"}", 
      "timestamp": 1409936189.572, 
      "type": 2
    }
  }, 
  "edu.mit.media.funf.probe.builtin.HardwareInfoProbe": {
    "_id": {
      "$oid": "5407294791cfc81dda355f43"
    }, 
    "key": "edu.mit.media.funf.probe.builtin.HardwareInfoProbe", 
    "time": 1409753650.223, 
    "value": {
      "androidid": "2bb389d1c126f737", 
      "bluetoothmac": "F8:F1:B6:3F:95:D2", 
      "brand": "motorola", 
      "deviceid": "353223054051801", 
      "model": "XT1053", 
      "timestamp": 1409753650.223, 
      "wifimac": "f8:f1:b6:3f:95:d3"
    }
  }, 
  "edu.mit.media.funf.probe.builtin.RunningApplicationsProbe": {
    "_id": {
      "$oid": "540a1d3791cfc86cda607ef5"
    }, 
    "key": "edu.mit.media.funf.probe.builtin.RunningApplicationsProbe", 
    "time": 1409948471.776, 
    "value": {
      "duration": 0.492, 
      "taskinfo": {
        "baseintent": {
          "maction": "android.intent.action.MAIN", 
          "mcategories": [
            "android.intent.category.HOME"
          ], 
          "mcomponent": {
            "mclass": "com.android.launcher2.Launcher", 
            "mpackage": "com.android.launcher"
          }, 
          "mflags": 274726912
        }, 
        "id": 1, 
        "persistentid": 1, 
        "stackid": 0
      }, 
      "timestamp": 1409948471.776
    }
  }, 
  "edu.mit.media.funf.probe.builtin.ScreenProbe": {
    "_id": {
      "$oid": "540a1d3791cfc86cda607ef4"
    }, 
    "key": "edu.mit.media.funf.probe.builtin.ScreenProbe", 
    "time": 1409948472.257, 
    "value": {
      "screen_on": False, 
      "timestamp": 1409948472.257
    }
  }, 
  "edu.mit.media.funf.probe.builtin.SimpleLocationProbe": {
    "_id": {
      "$oid": "540a2b2491cfc86cda608135"
    }, 
    "key": "edu.mit.media.funf.probe.builtin.SimpleLocationProbe", 
    "time": 1409951701.801, 
    "value": {
      "maccuracy": 82.178, 
      "maltitude": 0, 
      "mbearing": 0, 
      "mdistance": 0, 
      "melapsedrealtimenanos": {
        "$numberLong": "198152414229113"
      }, 
      "mhasaccuracy": True, 
      "mhasaltitude": False, 
      "mhasbearing": False, 
      "mhasspeed": False, 
      "minitialbearing": 0, 
      "misfrommockprovider": False, 
      "mlat1": 0, 
      "mlat2": 0, 
      "mlatitude": 42.3639962, 
      "mlon1": 0, 
      "mlon2": 0, 
      "mlongitude": -71.0797869, 
      "mprovider": "network", 
      "mresults": [
        0, 
        0
      ], 
      "mspeed": 0, 
      "mtime": {
        "$numberLong": "1409951701801"
      }, 
      "timestamp": 1409951701.801
    }
  }, 
  "edu.mit.media.funf.probe.builtin.SmsProbe": {
    "_id": {
      "$oid": "5409040e91cfc86cda60413d"
    }, 
    "key": "edu.mit.media.funf.probe.builtin.SmsProbe", 
    "time": 1409872540.311, 
    "value": {
      "address": "+17132018385", 
      "body": "{\"ONE_WAY_HASH\":\"6d7049b88568d8f67d8482c3e0db4726e9bd8036\"}", 
      "date": {
        "$numberLong": "1409872540311"
      }, 
      "locked": False, 
      "person": "581", 
      "protocol": 0, 
      "read": True, 
      "reply_path_present": False, 
      "service_center": "+12404492158", 
      "status": -1, 
      "thread_id": 10, 
      "timestamp": 1409872540.311, 
      "type": 1
    }
  }, 
  "edu.mit.media.funf.probe.builtin.WifiProbe": {
    "_id": {
      "$oid": "540a2b2491cfc86cda608133"
    }, 
    "key": "edu.mit.media.funf.probe.builtin.WifiProbe", 
    "time": 1409951679.608, 
    "value": {
      "bssid": "d8:9d:67:eb:4e:97", 
      "capabilities": "[ESS]", 
      "distancecm": -1, 
      "distancesdcm": -1, 
      "frequency": 2437, 
      "level": -79, 
      "ssid": "HP-Print-97-Officejet Pro 8600", 
      "timestamp": 1409951679.608, 
      "wifissid": {
        "octets": {
          "buf": [
            72, 
            80, 
            45, 
            80, 
            114, 
            105, 
            110, 
            116, 
            45, 
            57, 
            55, 
            45, 
            79, 
            102, 
            102, 
            105, 
            99, 
            101, 
            106, 
            101, 
            116, 
            32, 
            80, 
            114, 
            111, 
            32, 
            56, 
            54, 
            48, 
            48, 
            0, 
            0
          ], 
          "count": 30
        }
      }
    }
  }
}

iosuniques = {
# dateTime is converted to unix epoch time stamps
'battery': { 'datetime': '2014-08-28 13:51',
               'level': -100,
               'probe': 'battery',
               'state': 'unknown'}, #-> None. All Battery Probe values are lost

'deviceinfo': { 'brightness': 0.5078837, #-> ceiling function for ScreenProbe. True if > 0 else false 
                'country': 'en_US', #-> None. Values are lost
                'datetime': '2014-08-28 13:51',
                'device_model': 'iPhone', #-> HardwareInfoProbe.model
                'language': 'en', # -> None. Values are lost.
                'probe': 'deviceinfo',
                'system_version': '7.1.1' #-> Appent o HardwareInfoProbe.model
                },

'motion': { 'attitude_pitch': 0.733424593851337,
            'attitude_x': -0.2209912033994121,
            'attitude_yaw': 0.08644265799832047,
            'datetime': '2014-08-28 13:51',
            'gravity_x': -0.1628383100032806,
            'gravity_y': -0.6694176197052002,
            'gravity_z': -0.7248197793960571,
            'probe': 'motion',
            'rotationRate_x': 0.02880095317959785,
            'rotationRate_y': 0.5419228076934814,
            'rotationRate_z': 0.01222392171621323,
            'userAcceleration_x': 0.06832537800073624,
            'userAcceleration_y': 0.06832537800073624,
            'userAcceleration_z': 0.06832537800073624}, #-> Data from this probe is used to compute ActivityProbe. Don't insert it unless it's computed.

'positioning': { 'altitude': 224.4917755126953, #-> SimpleLocationProbe.maltitude
                 'course': -1, #->SimpleLocationProbe.mbearing
                 'datetime': '2014-08-28 13:51',
                 'horizontal_accuracy': 65, #-> SimpleLocationProbe.maccuracy
                 'lat': 30.35413728009769, #-> SimpleLocationProbe.mlatitude
                 'lon': -97.72731061603166, #-> SimpleLocationProbe.mlongitude
                 'probe': 'positioning',
                 'speed': -1,
                 'vertical_accuracy': 24.71350242576793 #-> None. Value is lost
                 }, #Be sure to fil in mprovider, mHasBearing, etc using iPhone values.

'proximity': { 'datetime': '2014-08-28 13:51',
               'probe': 'proximity',
               'state': False} # -> None. Value is lost.
}

mapping = {'screen_on': ['brightness'],
           'timestamp': ['datetime'],
           'model': ['device_model','system_version'],
           'maltitude': ['altitude'],
           'mbearing': ['course'],
           'maccuracy': ['horizontal_accuracy'],
           'mlatitude': ['lat'],
           'mlongitude': ['lon']}
           
keytype = {int: 0, float: 0.0, str: " ", dict: {},list: [], bool: False}
def getiosvalues(key):

    ioskey = mapping[key]
    iosvalues = {}
    returnvalue = []
    for x in iosuniques:
        iosvalues = dict(iosvalues.items() + iosuniques[x].items())
    #find all corresponding ios key for funf key
    for y in ioskey:
        #convert to unix epoch time
         if y == 'datetime':
             returnvalue = int(time.mktime(time.strptime(iosvalues[y], '%Y-%m-%d %H:%M'))) - time.timezone
         else:
             returnvalue.append(iosvalues[y])
    if type(returnvalue) is int:
        return returnvalue
    elif type(returnvalue[0]) is str:
        return ' '.join(returnvalue)


for x in funfuniques:
    #pdb.set_trace()
    probevalues=funfuniques[x]['value'].keys()
    for y in probevalues:
        
        if y in mapping:
            funfuniques[x]['value'][y] = getiosvalues(y)
        else:
            ytype = type(funfuniques[x]['value'][y])
            funfuniques[x]['value'][y]= keytype[ytype]
            
    print "\n"

print funfuniques
