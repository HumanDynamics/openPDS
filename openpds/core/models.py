from django.conf import settings
from django.db import models

class Profile(models.Model):
    uuid = models.CharField(max_length=36, unique=True, blank = False, null = False, db_index = True)

    def getDBName(self):
        return "User_" + str(self.uuid).replace("-", "_")
   
    def __unicode__(self):
        return self.uuid

class AuditEntry(models.Model):
    '''
    Represents an audit of a request against the PDS
    Given that there will be many entries (one for each request), 
    we are strictly limiting the size of data entered for each row
    The assumption is that script names and symbolic user ids
    will be under 64 characters 
    '''
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="auditentry_owner", db_index=True)
    requester = models.ForeignKey(Profile, blank = False, null = False, related_name="auditentry_requester", db_index=True)
    method = models.CharField(max_length=10)
    scopes = models.CharField(max_length=1024) # actually storing csv of valid scopes
    purpose = models.CharField(max_length=64, blank=True, null=True)
    script = models.CharField(max_length=64)
    token = models.CharField(max_length=64)
    system_entity_toggle = models.BooleanField()
    trustwrapper_result = models.CharField(max_length=64)
    timestamp = models.DateTimeField(auto_now_add = True, db_index=True)
    
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
    uri = models.URLField(blank = True, null = True)
    
    def __unicode__(self):
        self.pk

class Device(models.Model):

    datastore_owner = models.ForeignKey(Profile, blank=False, null=False, related_name="device_owner", db_index=True)
    gcm_reg_id = models.CharField(max_length=1024, blank=False, null=False)
