from oms_pds.internal.sql import SQLiteInternalDataStore
from oms_pds.internal.mongo import InternalDataStore
from oms_pds.internal.compound import CompoundInternalDataStore

def getInternalDataStore(profile, app_id, lab_id, token):
    return CompoundInternalDataStore(InternalDataStore(profile, app_id, lab_id, token), SQLiteInternalDataStore(profile, app_id, lab_id, token))
    
