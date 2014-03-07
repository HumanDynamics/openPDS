import uuid
import requests
from oms_pds.authentication import OAuth2Authentication
from oms_pds.authorization import PDSAuthorization
from tastypie import fields
from oms_pds.pds.models import Profile
from oms_pds.tastypie_mongodb.resources import MongoDBResource, Document
from oms_pds.meetup.internal import getInternalDataStore
from oms_pds.meetup.tasks import sendMeetupRequestToParticipants, notifyRequesterOfApprovalStatus
from gcm import GCM

class MeetupRequestResource(MongoDBResource):
    id = fields.CharField(attribute="_id")
    uuid = fields.CharField(attribute="uuid", unique=True, default=uuid.uuid4)
    requester = fields.CharField(attribute="requester", null=False)
    description = fields.CharField(attribute="description", null=False)
    participants = fields.ListField(attribute="participants", null=False)
    approved = fields.BooleanField(attribute="approved", null=True, blank=True, default=False)
    approvals = fields.ListField(attribute="approvals", null=True, blank=True, default=[])
    time = fields.CharField(attribute="time", null=True, blank=True)
    place = fields.ListField(attribute="place", null=True, blank=True)

    class Meta:
        # NOTE: We're using funf_write as the scope just so we don't have to add a new scope to all tokens that will be used for the app
        # moving forward, this should have its own scope of meetup_write, or something like that
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = False)
        collection = "meetup_request"
        resource_name = "meetup_request"
        list_allowed_methods = ["delete", "get", "post"]
        object_class = Document

    def obj_create(self, bundle, request = None, **kwargs):
        #pdb.set_trace()
        requester = bundle.data["requester"]
        owner = request.GET["datastore_owner__uuid"]
        token = request.GET["bearer_token"]
        profile = Profile.objects.get(uuid=owner)
        meetup=None

        if "uuid" in bundle.data:
            ids = getInternalDataStore(profile, token)
            meetup = ids.getMeetupRequest(bundle.data["uuid"])
        else:
            bundle.data["uuid"] = str(uuid.uuid4())
    
        if meetup is not None:
            # We're updating a pre-existing request instead of creating a new one... 
            kwargs["pk"] = meetup["_id"]            
            return self.obj_update(bundle, request, **kwargs)
        else:
            bundle.data["approved"] = bundle.data.get("approved", False)
            bundle.data["approvals"] = bundle.data.get("approvals", [])

        if requester == owner:
            # If we're the initiator, we need to notify the other participants...
            sendMeetupRequestToParticipants.apply_async(args=(bundle.data, token))

        #bundle.data["approved"] = True  # Owner requesting it implies approva
        return super(MeetupRequestResource, self).obj_create(bundle,request, **kwargs)

    def obj_update(self, bundle, request=None, **kwargs):
        owner = request.GET["datastore_owner__uuid"]
        token = request.GET["bearer_token"]
        meetup = self.obj_get(request, **kwargs)
        if meetup is not None and meetup["requester"] != owner and "approved" in bundle.data:
            # If the owner is not the requester, and this update is for approving the meetup, notify the requester
            current_approval = "approved" in meetup and meetup["approved"]
            requires_update = current_approval != bundle.data["approved"]
            meetup_uuid=meetup["uuid"]
            approved = bundle.data["approved"]
            requester = meetup["requester"]
            if requires_update:
                notifyRequesterOfApprovalStatus.apply_async(args=(meetup_uuid,requester,approved,owner, token))
        return super(MeetupRequestResource, self).obj_update(bundle, request, **kwargs)
