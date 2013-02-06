from django.conf import settings
from django.db import models
from mongoengine import *

connect(settings.MONGODB_DATABASE)


class Profile(models.Model):
    uuid = models.CharField(max_length=36, unique=True, blank = False, null = False, db_index = True)
    
    def __unicode__(self):
        return self.uuid

class ResourceKey(models.Model):
    ''' A way of controlling sharing within a collection.  Maps to any key within a collection.  For example, funf probes and individual answers to questions'''
    key = models.CharField(max_length=120)
    issharing = models.BooleanField(default=True)

class ProbeGroupSetting(models.Model):
    ''' A way of grouping resource keys for sharing.'''
    name = models.CharField(max_length=120)
    issharing = models.BooleanField(default=False)
    keys = models.ManyToManyField(ResourceKey) #a list of roles the user is currently sharing with

class Purpose(models.Model):
    name = models.CharField(max_length=120)
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="purpose_owner")
    
    def __unicode__(self):
        return self.name + "(" + self.datastore_owner.uuid + ")"

class Scope(models.Model):
    name = models.CharField(max_length=120)
    purpose = models.ManyToManyField(Purpose)
    issharing = models.BooleanField(default=False)
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="scope_owner")
    
    def __unicode__(self):
        return self.name + "(" + self.datastore_owner.uuid + ")"

class Role(models.Model):
    """ @name : The user defined name of the role
        @purpose : A list of purposes associated with this role
        @tokens : A list of oauth tokens of users assigned to this role """
    name = models.CharField(max_length=120)
    purpose = models.ManyToManyField(Purpose)
    issharing = models.BooleanField(default=False)
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="role_owner")
    
    def __unicode__(self):
        return self.name + "(" + self.datastore_owner.uuid + ")"
    # TODO: fill in field for tokens (rather than ints / uuids)

class SharingLevel(models.Model):
    level = models.IntegerField()
    purpose = models.ManyToManyField(Purpose)
    isselected = models.BooleanField(default=False)
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="sharinglevel_owner")
    
    def __unicode__(self):
        return str(self.level) + "(" + self.datastore_owner.uuid + ")"

class AuditEntry(models.Model):
    '''
    Represents an audit of a request against the PDS
    Given that there will be many entries (one for each request), 
    we are strictly limiting the size of data entered for each row
    The assumption is that script names and symbolic user ids
    will be under 64 characters 
    '''
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

class Notification(models.Model):
    '''
    Represents a notification about a user's data. This can be filled in while constructing answers
    '''
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="notification_owner")
    title = models.CharField(max_length = 64, blank = False, null = False)
    content = models.CharField(max_length = 1024, blank = False, null = False)
    type = models.IntegerField(blank = False, null = False)
    timestamp = models.DateTimeField(auto_now_add = True)
    
    def __unicode__(self):
        self.pk
