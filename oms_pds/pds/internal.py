import ast
import sqlite3
import os
import stat
import threading
from pymongo import Connection
from oms_pds.pds.models import Profile
from oms_pds.accesscontrol.models import Settings
from oms_pds import settings

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

INTERNAL_DATA_STORE_INSTANCES = {}

def getInternalDataStore(profile, token):
    try:
        internalDataStore = DualInternalDataStore(profile, token)
    except Exception as e:
        print str(e)
        internalDataStore = InternalDataStore(profile, token)
    return internalDataStore

def dict_factory(cursor, row):
    dataRow = False
    d = {}
    v = {}
    for idx, col in enumerate(cursor.description):
        if col[0] == "time":
            dataRow = True
            d["time"] = row[idx]
        else:
            v[col[0]] = row[idx]
    if dataRow:
        d["value"] = v
    else:
        d = v
    return d

def getColumnDefForTable(table):
    return  ", ".join([ name + " " + dataType for (name, dataType) in table["columns"]])

def getCreateStatementForTable(table):
    columnDef = getColumnDefForTable(table)
    statement = "create table if not exists %s (%s)" % (table["name"], columnDef)
    return statement

class ListWithCount(list):
    def count(self):
        return len(self)

def getColumnValueFromRawData(rawData, columnName, tableDef, source="funf"):    
    return tableDef["mapping"][source][columnName](rawData) if "mapping" in tableDef and source in tableDef["mapping"] and columnName in tableDef["mapping"][source] else rawData[columnName]

class SQLiteInternalDataStore:
    SQLITE_DB_LOCATION = settings.SERVER_UPLOAD_DIR + "dataStores/"
    
    INITIALIZED_DATASTORES = []

    LOCATION_TABLE = {
        "name": "LocationProbe",
        "columns": [
            ("mlatitude", "REAL"),
            ("mlongitude", "REAL"),
            ("maltitude", "REAL"), 
            ("maccuracy", "REAL"),
            ("mprovider", "TEXT")
        ]
    }

    ACTIVITY_TABLE = {
        "name": "ActivityProbe",
        "columns": [ 
            ("low_activity_intervals", "INTEGER"),
            ("high_activity_intervals", "INTEGER"),
            ("total_intervals", "INTEGER")
        ]
    }

    SCREEN_TABLE = {
        "name": "ScreenProbe",
        "columns": [
            ("screen_on", "INTEGER")
        ]
    }
   
    SMS_TABLE = {
        "name": "SmsProbe",
        "columns": [
            ("address", "TEXT"),
            ("person", "TEXT"),
            ("subject", "TEXT"),
            ("thread_id", "INTEGER"),
            ("body", "TEXT"),
            ("date", "INTEGER"),
            ("type", "INTEGER"),
            ("message_read", "INTEGER"),
            ("protocol", "INTEGER"),
            ("status", "INTEGER")
        ]
    }

    CALL_LOG_TABLE = {
        "name": "CallLogProbe",
        "columns": [
            ("_id", "INTEGER"),
            ("name", "TEXT"),
            ("number", "TEXT"),
            ("number_type", "TEXT"),
            ("date", "INTEGER"),
            ("type", "INTEGER"),
            ("duration", "INTEGER")
        ]
    }

    BLUETOOTH_TABLE = {
        "name": "BluetoothProbe",
        "columns": [
            ("class", "INTEGER"),
            ("bt_mac", "TEXT"),
            ("name", "TEXT"),
            ("rssi", "INTEGER")
        ],
        "mapping": {
            "funf": {
                "bt_mac": lambda d: d["android-bluetooth-device-extra-device"]["maddress"],
                "class": lambda d: d["android-bluetooth-device-extra-class"]["mclass"],
                "name": lambda d: d.get("android-bluetooth-device-extra-name", None),
                "rssi": lambda d: d["android-bluetooth-device-extra-rssi"] 
            }
        }
    }

    WIFI_TABLE = {
        "name": "WifiProbe",
        "columns": [
            ("bssid", "TEXT"),
            ("ssid","TEXT"),
            ("level", "INTEGER")
        ]
    }
    
    ANSWER_TABLE = {
        "name": "Answer",
        "columns": [
            ("key", "TEXT PRIMARY KEY"),
            ("value", "TEXT")
        ]
    }
    
    ANSWERLIST_TABLE = {
        "name": "AnswerList",
        "columns": [
            ("key", "TEXT PRIMARY KEY"),
            ("value", "TEXT")
        ]
    }

    DATA_TABLE_LIST = [WIFI_TABLE, BLUETOOTH_TABLE, CALL_LOG_TABLE, SMS_TABLE, ACTIVITY_TABLE, SCREEN_TABLE, LOCATION_TABLE]

    ANSWER_TABLE_LIST = [ANSWER_TABLE, ANSWERLIST_TABLE]

    def __init__(self, profile, token):
        self.profile = profile
        #print profile.uuid
        fileName = SQLiteInternalDataStore.SQLITE_DB_LOCATION + profile.getDBName() + ".db"
        self.db = sqlite3.connect(fileName)
        self.db.row_factory = dict_factory

        #Not perfect, since we're still initializing the DBs once per run, it's still better than running the following every time
        if profile not in SQLiteInternalDataStore.INITIALIZED_DATASTORES:
            SQLiteInternalDataStore.INITIALIZED_DATASTORES.append(profile)
            try:
                os.chmod(fileName, stat.S_IREAD | stat.S_IWRITE | stat.S_IEXEC | stat.S_IRWXO | stat.S_IRWXU | stat.S_IRWXG)
            except:
                #this is expected if the user accessing the db isn't the one who owns the file
                pass
            c = self.db.cursor()
            # We probably don't want to run the table creation every time (even if we're checking for existence). 
            # Make this a setup / initialization method that we run once when a PDS is set up
            for table in SQLiteInternalDataStore.DATA_TABLE_LIST:
                if next((c for c in table["columns"] if c[0] == "time"), None) is None:
                    table["columns"].append(("time", "REAL PRIMARY KEY"))
                createStatement = getCreateStatementForTable(table)
                c.execute(createStatement)
    
            for table in SQLiteInternalDataStore.ANSWER_TABLE_LIST:
                c.execute(getCreateStatementForTable(table))
            self.db.commit()

    def getAnswerFromTable(self, key, table):
        #table = "AnswerList" if isinstance(data, list) else "Answer"
        statement = "select key,value from %s where key=?" % table
        c = self.db.cursor()
        c.execute(statement, (key,))
        result = c.fetchone()
        return ListWithCount([{ "key": result["key"], "value": ast.literal_eval(result["value"]) }]) if result is not None else None

    def getAnswer(self, key):
        return self.getAnswerFromTable(key, "Answer")

    def getAnswerList(self, key):
        return self.getAnswerFromTable(key, "AnswerList")

    def saveAnswer(self, key, data):
        table = "AnswerList" if isinstance(data, list) else "Answer"
        statement = "insert or replace into %s(key, value) values(?, ?)" % table
        c = self.db.cursor()
        c.execute(statement, (key, "%s"%data))
        self.db.commit()
    
    def getData(self, key, startTime, endTime):
        table = key # A simplification for now
        statement = "select * from %s" % table
        times = ()

        if startTime is not None or endTime is not None:
            statement += " where "
            if startTime is not None: 
                times = (startTime,)
                statement += "time >= ?" 
                statement += " and " if endTime is not None else ""
            if endTime is not None:
                times = times + (endTime,)
                statement += "time < ?"

        c = self.db.cursor()
        c.execute(statement, times)
        return ListWithCount(c.fetchall())
    
    def saveData(self, data):
        # Again, assuming only funf data at the moment...
        tableName = data["key"].rpartition(".")[2]
        time = data["time"]
        dataValue = data["value"]
        table = next((t for t in SQLiteInternalDataStore.DATA_TABLE_LIST if tableName.endswith(t["name"])), None)
        if table is None:
            return False
        wildCards = ("?," * len(table["columns"]))[:-1]
        columnValues = []
        for columnName in [t[0] for t in table["columns"]]:
            value = time if columnName == "time" else getColumnValueFromRawData(dataValue, columnName, table, "funf")
            columnValues.append(value)
        statement = "insert into %s(%s) values(%s)" % (table["name"], ",".join([c[0] for c in table["columns"]]), wildCards)
        self.db.execute(statement, tuple(columnValues))
        self.db.commit()
    
class InternalDataStore:
    def __init__(self, profile, token):
        # This should check the token and pull down approved scopes for it
        self.profile = profile
        self.db = connection[profile.getDBName()]

    def saveAnswer(self, key, data):
        collection = self.db["answerlist"] if isinstance(data, list) else self.db["answer"]

        answer = collection.find({ "key": key })
        if answer.count() == 0:
            answer = { "key": key }
        else:
            answer = answer[0]
        
        answer["value"] = data
        collection.save(answer)
    
    def getAnswer(self, key):
        return self.db["answer"].find({ "key": key })

    def getAnswerList(self, key):
        return self.db["answerlist"].find({"key": key })

    def getData(self, key, startTime, endTime):
        # In this case, we're assuming the only source is Funf
        dataFilter = {"key": {"$regex": key+"$"}}
        if startTime is not None or endTime is not None:
            timeFilter = {}
            if startTime is not None:
                timeFilter["$gte"] = startTime
            if endTime is not None:
                timeFilter["$lt"] = endTime
            dataFilter["time"] = timeFilter
        return self.db["funf"].find(dataFilter)
    
    def saveData(self, data):
        self.db["funf"].save(data)

class DualInternalDataStore:
    def __init__(self, profile, token):
        self.ids = InternalDataStore(profile, token)
        self.sids = SQLiteInternalDataStore(profile, token)

    def saveAnswer(self, key, data):
        self.ids.saveAnswer(key, data)
        self.sids.saveAnswer(key, data)

    def getAnswer(self, key):
        return self.ids.getAnswer(key)

    def getAnswerList(self, key):
        return self.ids.getAnswerList(key)

    def getData(self, key, startTime, endTime):
        return self.ids.getData(key, startTime, endTime)

    def saveData(self, data):
        self.ids.saveData(data)
        self.sids.saveData(data)

class AccessControlledInternalDataStore:
    def __init__(self, profile, token, app_id, lab_id, service_id):
	self.profile = profile
	self.datastore_owner_id = self.profile.id
	self.app_id = app_id
	self.lab_id = lab_id
	self.service_id = service_id
	#self.enabled = check and set

    def getData(self, probe, startTime, endTime):

	enabled_flag = False
	probe_flag = False
	#object.find()
	#dictionary mapping, no rows returned --> empty set of data. 
	for settings in Settings.objects.raw('SELECT * FROM accesscontrol_settings WHERE app_id = %s AND lab_id = %s AND service_id = %s ', [self.app_id, self.lab_id, self.service_id]):
		enabled_flag = settings.enabled
		if 'activity' in probe:
			probe_flag = settings.activity_probe
		elif 'sms' in probe:
			probe_flag = settings.sms_probe
		elif 'call_log' in probe:		
			probe_flag = settings.call_log_probe
		elif 'bluetooth' in probe:
			probe_flag = settings.bluetooth_probe
		elif 'wifi' in probe:
			probe_flag = settings.wifi_probe
		elif 'simple_location' in probe:
			probe_flag = settings.simple_location_probe
		elif 'screen' in probe:
			probe_flag = settings.screen_probe
		elif 'running_applications' in probe:	
			probe_flag = settings.running_applications_probe
		elif 'hardware_info' in probe:
			probe_flag = settings.hardware_info_probe
		elif 'app_usage' in probe:
			probe_flag = settings.app_usage_probe

	if enabled_flag and probe_flag:
		return getDataInternal(probe, startTime, endTime)
	else:
		return None
	
			
def getAccessControlledInternalDataStore(profile, token, app_id, lab_id, service_id):
    try:
        internalDataStore = AccessControlledInternalDataStore(profile, token, app_id, lab_id, service_id)
    except Exception as e:
	internalDataStore = None
        print str(e)
    return internalDataStore

def getDataInternal(probe, startTime, endTime):
	return True
