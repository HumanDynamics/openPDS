from oms_pds.accesscontrol.internal import AccessControlledInternalDataStore


class CompoundInternalDataStore:

    def __init__(self, ids1, ids2):
        self.ids1 = ids1
        self.ids2 = ids2

    def getData(self, key, start, end):
        return self.ids1.getData(key, start, end)
   
    def getAnswer(self, key):
        return self.ids1.getAnswer(key)

    def getAnswerList(self, key):
        return self.ids1.getAnswerList(key)

    def saveData(self, data):
        self.ids1.saveData(data)
        self.ids2.saveData(data)
    
    def saveAnswer(self, key, answer):
        self.ids1.saveAnswer(key, answer)
        self.ids2.saveAnswer(key, answer)

    def notify(self, notificationType, title, content, uri):
        return self.ids1.notify(notificationType, title, content, uri)
