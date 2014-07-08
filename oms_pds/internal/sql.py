import ast
import sqlite3
import os
import stat
import threading
import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from pymongo import Connection
from oms_pds.pds.models import Profile
from oms_pds.accesscontrol.models import Settings
from oms_pds.accesscontrol.internal import AccessControlledInternalDataStore, getAccessControlledInternalDataStore
from oms_pds import settings

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

INTERNAL_DATA_STORE_INSTANCES = {}

def getInternalDataStore(profile, app_id, lab_id, token):
    try:
        internalDataStore = DualInternalDataStore(profile, app_id, lab_id, token)
    except Exception as e:
        print str(e)
        internalDataStore = InternalDataStore(profile, app_id, lab_id, token)
    return internalDataStore

def dict_factory(cursor, row):
    dataRow = False
    d = {}
    v = {}
    for idx, col in enumerate(cursor.description):
        if col[0] == "time":
            dataRow = True
            d["time"] = row[idx]
        elif col[0] == "key": 
            d["key"] = row[idx]
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
    return tableDef["mapping"][source][columnName](rawData) if "mapping" in tableDef and source in tableDef["mapping"] and columnName in tableDef["mapping"][source] else rawData[columnName] if columnName in rawData else None

class SQLInternalDataStore(AccessControlledInternalDataStore):
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
            ("date", "BIGINT"),
            ("type", "INTEGER"),
            ("message_read", "INTEGER"),
            ("protocol", "INTEGER"),
            ("status", "INTEGER")
        ],
        "mapping": {
            "funf": {
                "message_read": lambda d: d["read"]
            }
        }
    }

    CALL_LOG_TABLE = {
        "name": "CallLogProbe",
        "columns": [
            ("_id", "INTEGER"),
            ("name", "TEXT"),
            ("number", "TEXT"),
            ("number_type", "TEXT"),
            ("date", "BIGINT"),
            ("type", "INTEGER"),
            ("duration", "INTEGER")
        ],
        "mapping": {
            "funf": {
                "number_type": lambda d: d["numbertype"]
            }
        }
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

    def getAnswerFromTable(self, key, table):
        #table = "AnswerList" if isinstance(data, list) else "Answer"
        statement = "select key,value from %s where key=%s" %(table, self.getVariablePlaceholder())
        c = self.getCursor()
        c.execute(statement, (key,))
        result = c.fetchone()
        return ListWithCount([{ "key": result["key"], "value": ast.literal_eval(result["value"]) }]) if result is not None else None

    def getAnswer(self, key):
        return self.getAnswerFromTable(key, "Answer")

    def getAnswerList(self, key):
        return self.getAnswerFromTable(key, "AnswerList")

    def saveAnswer(self, key, data):
        table = "AnswerList" if isinstance(data, list) else "Answer"
        p = self.getVariablePlaceholder()
        statement = "insert or replace into %s(key, value) values(%s, %s)" %(table,p,p)
        c = self.getCursor()
        c.execute(statement, (key, "%s"%data))
        self.db.commit()
        c.close()
    
    def getDataInternal(self, key, startTime, endTime):
        table = key # A simplification for now
        statement = "select '%s' as key,* from %s" %(key,table)
        times = ()

        if startTime is not None or endTime is not None:
            statement += " where "
            if startTime is not None: 
                times = (startTime,)
                statement += "time >= %s" % self.getVariablePlaceholder()
                statement += " and " if endTime is not None else ""
            if endTime is not None:
                times = times + (endTime,)
                statement += "time < %s" % self.getVariablePlaceholder()

        c = self.getCursor()
        c.execute(statement, times)
        return ListWithCount(c.fetchall())
    
    def saveData(self, data):
        # Again, assuming only funf data at the moment...
        tableName = data["key"].rpartition(".")[2]
        source = "funf" if data["key"].rpartition(".")[0].startswith("edu.mit.media.funf") else "sql"
        time = data["time"]
        dataValue = data["value"]
        table = next((t for t in SQLiteInternalDataStore.DATA_TABLE_LIST if tableName.endswith(t["name"])), None)
        if table is None:
            return False
        wildCards = (("%s,"%self.getVariablePlaceholder()) * len(table["columns"]))[:-1]
        columnValues = []
        for columnName in [t[0] for t in table["columns"]]:
            value = time if columnName == "time" else getColumnValueFromRawData(dataValue, columnName, table, source)
            columnValues.append(value)
        statement = "insert into %s(%s) values(%s)" % (table["name"], ",".join([c[0] for c in table["columns"]]), wildCards)
        print statement
        print columnValues
        c = self.getCursor()
        c.execute(statement, tuple(columnValues))
        self.db.commit()
        c.close()

    def getCursor(self):
        raise NotImplementedError("Subclasses must specify how to get a cursor.")

    def getVariablePlaceholder(self):
        raise NotImplementedError("Subclasses must specify a variable placeholder.")

class SQLiteInternalDataStore(SQLInternalDataStore):
    SQLITE_DB_LOCATION = settings.SERVER_UPLOAD_DIR + "dataStores/"
    
    INITIALIZED_DATASTORES = []

    def __init__(self, profile, app_id, lab_id, token):
        super(SQLiteInternalDataStore, self).__init__(profile, app_id, lab_id)
        self.profile = profile
        #print profile.uuid
        fileName = SQLiteInternalDataStore.SQLITE_DB_LOCATION + profile.getDBName() + ".db"
        self.db = sqlite3.connect(fileName)
        self.db.row_factory = dict_factory
        self.source = "sql"

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
            for table in SQLInternalDataStore.DATA_TABLE_LIST:
                if next((c for c in table["columns"] if c[0] == "time"), None) is None:
                    table["columns"].append(("time", "DOUBLE PRECISION PRIMARY KEY"))
                createStatement = getCreateStatementForTable(table)
                c.execute(createStatement)
    
            for table in SQLInternalDataStore.ANSWER_TABLE_LIST:
                c.execute(getCreateStatementForTable(table))
            self.db.commit()

    def getCursor(self):
        return self.db.cursor()

    def getVariablePlaceholder(self):
        return "?"

class PostgresInternalDataStore(SQLInternalDataStore):
    INITIALIZED_DATASTORES = []

    def __init__(self, profile, token):
        self.profile = profile
        self.token = token
        self.source = "sql"

        if profile not in PostgresInternalDataStore.INITIALIZED_DATASTORES:            
            PostgresInternalDataStore.INITIALIZED_DATASTORES.append(profile)
            try:
                init_conn = psycopg2.connect(user="postgres", password="p0stgre5", database=profile.getDBName().lower())
            except psycopg2.OperationalError:
                init_conn = psycopg2.connect(user="postgres", password="p0stgre5")
                init_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                init_cur = init_conn.cursor()
                init_cur.execute("create database %s;"%profile.getDBName())
                init_cur.close()
                init_conn.close()
                init_conn = psycopg2.connect(user="postgres", password="p0stgre5", database=profile.getDBName().lower())

            init_cur = init_conn.cursor()
            # We probably don't want to run the table creation every time (even if we're checking for existence). 
            # Make this a setup / initialization method that we run once when a PDS is set up
            for table in SQLInternalDataStore.DATA_TABLE_LIST:
                if next((c for c in table["columns"] if c[0] == "time"), None) is None:
                    table["columns"].append(("time", "DOUBLE PRECISION PRIMARY KEY"))
                createStatement = getCreateStatementForTable(table)
                init_cur.execute(createStatement)

            for table in SQLInternalDataStore.ANSWER_TABLE_LIST:
                init_cur.execute(getCreateStatementForTable(table))
            init_conn.commit()
            init_cur.close()
            init_conn.close()
        self.db = psycopg2.connect(user="postgres", password="p0stgre5", database=profile.getDBName().lower())
    
    def getCursor(self):
        return self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    def getVariablePlaceholder(self):
        return "%s" 
