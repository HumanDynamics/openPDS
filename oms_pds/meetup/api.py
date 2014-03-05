from oms_pds.authentication import OAuth2Authentication
from oms_pds.authorization import PDSAuthorization
from tastypie import fields
from oms_pds.tastypie_mongodb.resources import MongoDBResource, Document
from gcm import GCM

class MeetupRequestResource(MongoDBResource):
    id = fields.CharField(attribute="_id")
    uuid = fields.CharField(attribute="uuid", null=False)
    requester = fields.CharField(attribute="requester", null=False)
    description = fields.CharField(attribute="description", null=False)
    participants = fields.ListField(attribute="participants", null=False)

    class Meta:
        # NOTE: We're using funf_write as the scope just so we don't have to add a new scope to all tokens that will be used for the app
        # moving forward, this should have its own scope of meetup_write, or something like that
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = False)
        collection = "meetup_request"
        resource_name = "meetup_request"
        list_allowed_methods = ["delete", "get", "post"]
        object_class = Document
