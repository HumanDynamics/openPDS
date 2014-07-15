import time
from datetime import date, timedelta
from oms_pds.internal.mongo import getInternalDataStore
from oms_pds.pds.models import Profile

def getStartTime(daysAgo, startAtMidnight):
    currentTime = time.time()
    return time.mktime((date.fromtimestamp(currentTime) - timedelta(days=daysAgo)).timetuple()) if startAtMidnight else currentTime - daysAgo * 24 * 3600

@task():
def computeFingerprint(ids): 
    lastWeek = getStartTime(6, False)
    for ap in ids.getData("WifiProbe", lastWeek, None):
