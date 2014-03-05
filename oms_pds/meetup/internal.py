from oms_pds.pds.internal import InternalDataStore

class MeetupInternalDataStore(InternalDataStore):
    # NOTE: This class depends on Mongo APIs and as such, only works with the Mongo IDS
    # Moving forward, this should change to support any IDS implementation
    def addParticipantToMeetupRequest(self, meetup_uuid, participant_uuid):
        meetup = self.getMeetupRequest(meetup_uuid)
        meetup = meetup if meetup is not None else { "uuid": meetup_uuid, "approvals": [participant_uuid] }
        if participant_uuid not in meetup["approvals"]: 
            meetup["approvals"].append(participant_uuid)
        self.db["meetup_request"].save(meetup)

    def approveMeetupRequest(self, meetup_uuid):
        meetup = self.getMeetupRequest(meetup_uuid)
        meetup = meetup if meetup is not None else { "uuid": meetup_uuid }
        meetup["approved"] = True
        self.db["meetup_request"].save(meetup)

    def addMeetupRequest(self, meetup_uuid, requester_uuid, participant_uuids, description):    
        meetup = self.getMeetupRequest(meetup_uuid)
        meetup = meetup if meetup is not None else { "uuid": meetup_uuid, "requester": requester_uuid, "participants": participant_uuids, "description": description, "approvals": []}
        self.db["meetup_request"].save(meetup)

    def getMeetupRequest(self, uuid):
        return self.db["meetup_request"].find_one({"uuid": uuid})

def getInternalDataStore(profile, token):
    return MeetupInternalDataStore(profile, token)

