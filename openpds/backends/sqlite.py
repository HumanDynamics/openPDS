import ast
import sqlite3
import os
import stat
import threading
import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from openpds.core.models import Profile
from openpds.accesscontrol.models import Settings
from openpds.accesscontrol.internal import AccessControlledInternalDataStore, getAccessControlledInternalDataStore
from openpds.backends.sql import dict_factory, getColumnDefForTable, getCreateStatementForTable, ListWithCount, getColumnValueFromRawData, SQLInternalDataStore
from openpds import settings

def getInternalDataStore(profile, app_id, lab_id, token):
    return SQLiteInternalDataStore(profile, app_id, lab_id, token)

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

