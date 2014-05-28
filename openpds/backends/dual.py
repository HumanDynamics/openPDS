from openpds.backends.sql import SQLiteInternalDataStore
from openpds.backends..mongo import InternalDataStore
from openpds.backends.compound import CompoundInternalDataStore

def getInternalDataStore(profile, app_id, lab_id, token):
    return CompoundInternalDataStore(InternalDataStore(profile, app_id, lab_id, token), SQLiteInternalDataStore(profile, app_id, lab_id, token))
    
