from pymongo import Connection
from oms_pds.pds.models import Profile
from oms_pds import settings

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

class InternalDataStore:
    def __init__(self, profile, token):
        # This should check the token and pull down approved scopes for it
        #self.profile = Profile.objects.get(uuid = uuid)
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
