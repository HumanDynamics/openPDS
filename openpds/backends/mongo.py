from pymongo import Connection
from openpds.core.models import Profile
from openpds.backends.base import InternalDataStore
from openpds import settings
import pdb

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

def getInternalDataStore(profile, app_id, lab_id, token):
    return MongoInternalDataStore(profile, app_id, lab_id, token)

class MongoInternalDataStore(InternalDataStore):
    def __init__(self, profile, app_id, lab_id, token):
    	"""
    	Initialize an InternalDataStore holding the user's data specified by profile, with authorization provided via token. 
   	 """
        super(MongoInternalDataStore, self).__init__(profile, app_id, lab_id, token)
        # This should check the token and pull down approved scopes for it
        self.profile = profile
        self.db = connection[profile.getDBName()]

    def saveAnswer(self, key, data):
    	"""
    	Saves the given data as an answer with the given key
    	"""
        collection = self.db["answerlist"] if isinstance(data, list) else self.db["answer"]

        answer = collection.find({ "key": key })
        if answer.count() == 0:
            answer = { "key": key }
        else:
            answer = answer[0]
        
        answer["value"] = data
        collection.save(answer)
    
    def getAnswer(self, key):
    	"""
    	Retrieves a dictionary representing the answer associated with a given answer key, if it exists or None if it doesn't. 
    	"""
        return self.db["answer"].find({ "key": key }) if key is not None else self.db["answer"].find()

    def getAnswerList(self, key):
    	"""
    	Retrieves a list representing the answer associated with a given answer key, if it exists or None if it doesn't.
    	"""
        return self.db["answerlist"].find({"key": key }) if key is not None else self.db["answerlist"].find()

    def getData(self, key, startTime, endTime):
    	"""
    	Gets data of a given type, denoted by key, that was recorded between startTime and endTime, or an empty list if no such data exists. 
    	"""
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

    # saves data to specified database
    def saveData(self, data, database):
    	"""
    	Saves data to this InternalDataStore. Data must provide a key and time in order to be retrieved for later use. 
    	"""
        self.db[database].save(data)

