from django.conf import settings
from django.db import models
from mongoengine import *

connect(settings.MONGODB_DATABASE)


class Purpose(Document):
    name = StringField(max_length=120, required=True)
#    author = ReferenceField(User)

class Scope(Document):
    name = StringField(max_length=120, required=True)
    purpose = ReferenceField(Purpose)

class Role(Document):
    """ @name : The user defined name of the role
	@purpose : A list of purposes associated with this role
	@tokens : A list of oauth tokens of users assigned to this role """
    name = StringField(max_length=120, required=True)
    purpose = ReferenceField(Purpose)

class SharingLevel(Document):
    level = IntField(required=True)
    purpose = ReferenceField(Purpose)

class Tokens(Document):
    id = StringField(required=True)
    roles = ListField(ReferenceField(Role))


class Profile(models.Model):
    uuid = models.CharField(max_length=36, unique=True, blank = False, null = False, db_index = True)

# Represents an audit of a request against the PDS
# Given that there will be many entries (one for each request), 
# we are strictly limiting the size of data entered for each row
# The assumption is that script names and symbolic user ids
# will be under 64 characters 
class AuditEntry(models.Model):
    
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="auditentry_owner")
    requester = models.ForeignKey(Profile, blank = False, null = False, related_name="auditentry_requester")
    method = models.CharField(max_length=10)
    scopes = models.CharField(max_length=1024) # actually storing csv of valid scopes
    purpose = models.CharField(max_length=64, blank=True, null=True)
    script = models.CharField(max_length=64)
    token = models.CharField(max_length=64)
    system_entity_toggle = models.BooleanField()
    trustwrapper_result = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add = True)
    
    def __unicode__(self):
        self.pk