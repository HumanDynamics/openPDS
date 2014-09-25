import ast
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
    return PostgresInternalDataStore(profile, app_id, lab_id, token)

class PostgresInternalDataStore(SQLInternalDataStore):
    INITIALIZED_DATASTORES = []

    def __init__(self, profile, app_id, lab_id, token):
        self.profile = profile
        self.token = token
        self.source = "sql"

        if profile not in PostgresInternalDataStore.INITIALIZED_DATASTORES:            
            PostgresInternalDataStore.INITIALIZED_DATASTORES.append(profile)
            try:
                init_conn = psycopg2.connect(user=settings.STORAGE_BACKEND["USER"], password=settings.STORAGE_BACKEND["PASSWORD"], database=profile.getDBName().lower())
            except psycopg2.OperationalError:
                init_conn = psycopg2.connect(user=settings.STORAGE_BACKEND["USER"], password=settings.STORAGE_BACKEND["PASSWORD"])
                init_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                init_cur = init_conn.cursor()
                init_cur.execute("create database %s;"%profile.getDBName())
                init_cur.close()
                init_conn.close()
                init_conn = psycopg2.connect(user=settings.STORAGE_BACKEND["USER"], password=settings.STORAGE_BACKEND["PASSWORD"], database=profile.getDBName().lower())

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
        self.db = psycopg2.connect(user=settings.STORAGE_BACKEND["USER"], password=settings.STORAGE_BACKEND["PASSWORD"], database=profile.getDBName().lower())
    
    def getCursor(self):
        return self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    def getVariablePlaceholder(self):
        return "%s" 
