from pymongo import Connection
from openpds.core.models import Profile
from openpds import settings

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

def getInternalDataStore(profile, app_id, lab_id, token):
    return InternalDataStore(profile, app_id, lab_id, token)

class InternalDataStore(object):
    def __init__(self, profile, app_id, lab_id, token):
    	"""
    	Initialize an InternalDataStore holding the user's data specified by profile, with authorization provided via token. 
   	    """
        # This should check the token and pull down approved scopes for it
        self.profile = profile
        self.app_id = app_id
        self.lab_id = lab_id
        self.token = token
 
    def saveAnswer(self, key, data):
    	"""
    	Saves the given data as an answer with the given key
    	"""
        pass
   
    def getAnswer(self, key):
    	"""
    	Retrieves a dictionary representing the answer associated with a given answer key, if it exists or None if it doesn't. 
    	"""
        pass

    def getAnswerList(self, key):
    	"""
    	Retrieves a list representing the answer associated with a given answer key, if it exists or None if it doesn't.
    	"""
        pass

    def getData(self, key, startTime, endTime):
    	"""
    	Gets data of a given type, denoted by key, that was recorded between startTime and endTime, or an empty list if no such data exists. 
    	"""
        pass 
   
    def saveData(self, data):
    	"""
    	Saves data to this InternalDataStore. Data must provide a key and time in order to be retrieved for later use. 
    	"""
        pass
