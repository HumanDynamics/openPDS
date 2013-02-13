from tastypie.authorization import Authorization
from oms_pds.authentication import OAuth2Authentication
from oms_pds.pds.models import Profile, AuditEntry

import settings
import pdb

class PDSAuthorization(Authorization):
    audit_enabled = True
    scope = ""
    requester_uuid = ""
    
    def requester(self):
        print self.requester_uuid
        return self.requester_uuid

    def trustWrapper(self, datastore_owner):
        print "checking trust wrapper"
        #ds_owner_profile = Profile.objects.get(uuid = datastore_owner_uuid)
        #print datastore_owner.sharinglevel_owner.get(isselected = True)

    def is_authorized(self, request, object=None):
        print "is authorized?"
        authenticator = OAuth2Authentication(self.scope)
        token = request.REQUEST["bearer_token"] if "bearer_token" in request.REQUEST else request.META["HTTP_BEARER_TOKEN"]
        # Result will be the uuid of the requesting party
        
        # Note: the trustwrapper must be run regardless of if auditting is enabled on this call or not
        
        datastore_owner_uuid = request.REQUEST["datastore_owner__uuid"]
        datastore_owner, ds_owner_created = Profile.objects.get_or_create(uuid = datastore_owner_uuid)
        self.requester_uuid = authenticator.get_userinfo_from_token(token, self.scope)
        self.trustWrapper(datastore_owner)
        
        print self.requester_uuid
        try:
            if (self.audit_enabled):
                #pdb.set_trace()
                audit_entry = AuditEntry(token = token)
                audit_entry.method = request.method
                audit_entry.scope = self.scope
                audit_entry.purpose = request.REQUEST["purpose"] if "purpose" in request.REQUEST else ""
                audit_entry.system_entity_toggle = request.REQUEST["system_entity"] if "system_entity" in request.REQUEST else False
                # NOTE: datastore_owner and requester are required
                # if they're not available, the KeyError exception should raise and terminate the request
                audit_entry.datastore_owner = datastore_owner
                audit_entry.requester, created = Profile.objects.get_or_create(uuid = self.requester_uuid)
                audit_entry.script = request.path
                audit_entry.save()
        except Exception as e:
            print e
        
        return True

    def __init__(self, scope, audit_enabled = True):
        #pdb.set_trace()
        self.scope = scope
        self.audit_enabled = audit_enabled
    
    # Optional but useful for advanced limiting, such as per user.
    # def apply_limits(self, request, object_list):
    #    if request and hasattr(request, 'user'):
    #        return object_list.filter(author__username=request.user.username)
    #
    #    return object_list.none()

