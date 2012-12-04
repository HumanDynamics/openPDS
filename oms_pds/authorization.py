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

    def trustWrapper(self, datastore_owner_uuid):
	print "checking trust wrapper"
        ds_owner_profile = Profile.objects.get(uuid = datastore_owner_uuid)
	print ds_owner_profile.sharinglevel_owner.get(isselected = True)

#>>> p0.role_owner.latest("id")
#<Role: Role object>
#>>> p0.role_owner.latest("id").name
#u'Care_Team'
#>>> p0.sharinglevel_owner.filter(isselected = True)
#[<SharingLevel: SharingLevel object>]
#>>> p0.sharinglevel_owner.filter(isselected = True).level
#Traceback (most recent call last):
#  File "<input>", line 1, in <module>
#AttributeError: 'QuerySet' object has no attribute 'level'
#>>> sl = p0.sharinglevel_owner.first(isselected = True)
#Traceback (most recent call last):
#  File "<input>", line 1, in <module>
#AttributeError: 'RelatedManager' object has no attribute 'first'
#>>> sl = p0.sharinglevel_owner.filter(isselected = True)
#>>> sl.latest("id")
#<SharingLevel: SharingLevel object>
#>>> sl.latest("id").level
 
    def is_authorized(self, request, object=None):
	print "is authorized?"
        authenticator = OAuth2Authentication(self.scope)
        token = request.REQUEST["bearer_token"] if "bearer_token" in request.REQUEST else request.META["HTTP_BEARER_TOKEN"]
        # Result will be the uuid of the requesting party
        self.requester_uuid = authenticator.get_userinfo_from_token(token, self.scope)
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
                datastore_owner_uuid = request.REQUEST["datastore_owner"]
		self.trustWrapper(datastore_owner_uuid)
                audit_entry.datastore_owner, created = Profile.objects.get_or_create(uuid = datastore_owner_uuid)
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






#import pymongo
#import logging
#from pymongo import Connection
#import json
#
##TODO This trust wrapper implements sharing as defined in DARPA DCAPS project.  Eventually we will need to implement sharing fully defined at the PDS level, and not a shared database.
#
##To install this trustwrapper on a resourceServer, run install_trustWrapper.py, which is located in the same directory as this file.
#
#
#def getPDSSharingLevel(db):
#    return sharing_level
#
# 
#def checkTrustWrapper( purpose, ro_sid=None, permitted_roles=None):
#    #ro_sid - the resource owner's symbolic key (also the postfix of the mongo store)
#    #id - the requester's id (used for mapping the role relationship)
#    #purpose - 'purpose' defined in SDD
#
#    logging.debug('resource owner symbolic ID')
#    logging.debug(ro_sid)
#    if ro_sid is None:
#	logging.debug('access request self...returning')
#        return True
#
#    try:
#	#TODO When PDS' are distributed, the database will be known implicitly
#
#	#sharing_level = getPDSSharingLevel(db)
#	sharing_level = 3
#
#
#	#TODO We will need to define application parameters where we can hold a list of installled applications, and create application specific stores on the fly
#	connection = Connection()
#        db_RA = connection["RealityAnalysis"]
#
#	#check sharing -> purpose
#	logging.debug("checking sharing to purpose")
#	logging.debug(sharing_level)
#	logging.debug(purpose)
#	if (db_RA.mapping.find_one({"SHARING": int(sharing_level), "PURPOSE": str(purpose)}) is not None):
#	    #TODO: check system entity toggle
#
#	    #check purpose -> role
#	    logging.debug("checking purpose to role")
#	    logging.debug(purpose)
#            for role in permitted_roles:
#		logging.debug(role)
#                if (db_RA.mapping.find_one({"ROLE":str(role), "PURPOSE": str(purpose)}) is not None):
#                     return True
#	    raise Exception("couldn't find a mapping for purpose - role")
#	else:
#	    raise Exception("couldn't find a mapping for sharing -> purpose")
#
#    except TypeError as e:
#        logging.debug('ERROR: personalPermissions store is not configured correctly.  Check that the collection "personalPermissions" exists, as well as entries for key-value "permission_type"-"sharing" as well as sub element object keys for "sharing" and "uidRoles"')
#        logging.debug(e.message)
#    finally:
#        connection.disconnect()
#    return False
