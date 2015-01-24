from django.conf import settings
from django.db import models
from mongoengine import *
from django.utils import simplejson

connect(settings.MONGODB_DATABASE)

GOAL_CHOICES = (
    ('s','smoking'),
    ('e','eating better'),
    ('t','stress reduction'),
    ('f','footcare'),
    ('n','none selected'),
)

STUDY_STATUS_CHOICES = (
    ('n', 'Not in study'),
    ('c', 'Control'),
    ('i', 'Intervention'),
    ('t', 'Test'),
)

class Profile(models.Model):
    uuid = models.CharField(max_length=36, unique=True, blank = False, null = False, db_index = True)
    wake = models.TimeField(default="8:00")
    sleep = models.TimeField(default="23:00")
    goal = models.CharField(max_length=1, choices=GOAL_CHOICES, default='n')
    study_status = models.CharField(max_length=1, choices=STUDY_STATUS_CHOICES, default='n')
    created = models.DateTimeField(auto_now_add=True)

    def getDBName(self):
        return "User_" + str(self.uuid).replace("-", "_")
   
    def __unicode__(self):
        return self.uuid
    
class QuestionType(models.Model):
    UI_CHOICES = (
        ('s', 'Slider'),
        ('b', 'Binary (Yes/No)'),
        ('m', 'Multiple Choice'),
    )
    
    goal = models.CharField(max_length=1, choices=GOAL_CHOICES, blank=True, null=True, help_text="this is only set if the question is a goal question. otherwise null")
    text = models.TextField() #What was your morning Glucose level?
    ui_type = models.CharField(max_length=1, choices=UI_CHOICES)
    params = models.TextField(default="[]", help_text="this column must be coded in JSON and is specific to the uitype - for YES/NO params=[], for slider params='[ [min, \"label\"], [max, \"label\"] ]' ie '[[ 0, \"worst\"], [10, \"best\"]]', Multiple Choice '[ [0, \"Never\"], [1, \"Some\"], [2, \"All\" ]]'")
    frequency_interval = models.IntegerField(default=1440, blank=True, null=True, help_text="minutes between the next time the question is asked. set as null if the question isn't set on a schedule directly.")
    resend_quantity = models.IntegerField(default=0, help_text="Number of times to resend this question until it's answered.")
    followup_key = models.IntegerField(blank=True, null=True, help_text="If this question result in a followup question, select the answer that results in a follow up. If not, or if any answer creates a follow up, leave blank")
    followup_question = models.ForeignKey('QuestionType', related_name="parent_question", blank=True, null=True, help_text="If this question should result in a followup question, select the follow-up question. If not, leave blank") 
    expiry = models.IntegerField(default=1440, help_text="minutes until the question expires")
    sleep_offset = models.IntegerField(default=0, help_text="minutes after a user wakes up to send notification. if negative, it's minutes before a user goes to sleep to send a notification.")
    intervention_only = models.BooleanField(default=True)
    
    
    def __unicode__(self):
        return unicode( str(self.pk) + ": " + self.text )
        
    def optionList(self):
        return simplejson.loads(self.params)
        
    def followup_question_parent(self):
        parents = self.parent_question.all()
        if len(parents) > 0:
            return parents[0]
        return None
        

class QuestionInstance(models.Model):
    question_type = models.ForeignKey('QuestionType')
    profile = models.ForeignKey('Profile')
    datetime = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    answer = models.IntegerField(blank=True, null=True)
    expired = models.BooleanField(default=False, help_text="Once an answer either expires past a certain time or is completed, this is checked off. This is for the efficiency of only querying the database on expired and profile.")
    notification_counter = models.IntegerField(default=0, help_text="How many times was a notification sent out for this Question Instance?")
#    followup_instance = models.ForeignKey('QuestionInstance', blank=True, null=True, help_text="If this question has a followup question associated, then reference it from here")
    def __unicode__(self):
        return str(self.datetime) + ": " +self.profile.__unicode__() + " (" +str(self.question_type.pk)+ ")"

class ResourceKey(models.Model):
    ''' A way of controlling sharing within a collection.  Maps to any key within a collection.  For example, funf probes and individual answers to questions'''
    key = models.CharField(max_length=120)
    issharing = models.BooleanField(default=True)
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name = "resourcekey_owner")

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
        return str(self.pk)

class Notification(models.Model):
    '''
    Represents a notification about a user's data. This can be filled in while constructing answers
    '''
    datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="notification_owner")
    title = models.CharField(max_length = 64, blank = False, null = False)
    content = models.CharField(max_length = 1024, blank = False, null = False)
#    content = models.TextField() # For SmartCATCH - use the content as a serialized json object
    type = models.IntegerField(blank = False, null = False)
    timestamp = models.DateTimeField(auto_now_add = True)
#    uri = models.URLField(blank = True, null = True)
    uri = models.TextField() # For SmartCATCH - use the uri as a serialized json object
#    json_content = models.TextField()
    
    def __unicode__(self):
        return str(self.pk)

class Device(models.Model):
    datastore_owner = models.ForeignKey(Profile, blank=False, null=False, related_name="device_owner", db_index=True)
    gcm_reg_id = models.CharField(max_length=1024, blank=False, null=False)
