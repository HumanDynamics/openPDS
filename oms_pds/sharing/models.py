from django.conf import settings
from django.db import models
from oms_pds.trust.models import Role, SharingLevel


class Tokens(models.Model):
    token_id = models.CharField(max_length=120)
    role = models.ManyToManyField(Role)  

class OverallSharingLevel(models.Model):
    level = models.IntegerField(default=0)

class ProbeGroupSetting(models.Model):
    name = models.CharField(max_length=120)
    issharing = models.BooleanField(default=False)
#    probes = ListField(ReferenceField(FunfResource))

#class Sharing(models.Model):
#    overallsharinglevel = models.ForeignKey(SharingLevel)
#    roles = models.ManyToManyField(Role) #a list of roles the user is currently sharing with
#    probes = models.ManyToManyField(ProbeGroupSetting)#a list of probes the user is currently sharing 

#class Space(Document):
#    """ @name : The user defined name of the role
#        @purpose : A list of purposes associated with this role
#        @tokens : A list of oauth tokens of users assigned to this role """
#    name = StringField(max_length=120, required=True)
#    purpose = ReferenceField(Purpose)
#
#class Time(Document):
#    level = IntField(required=True)
#    purpose = ReferenceField(Purpose)

