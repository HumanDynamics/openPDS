from django.conf import settings
from mongoengine import *
from oms_pds.pds.api import FunfResource
from oms_pds.trust.models import Role

connect(settings.MONGODB_DATABASE)


class Tokens(Document):
    token_id = StringField(max_length=120, required=True)
    role = ReferenceField(Role)  

class OverallSharingLevel(Document):
    level = IntField(required=True)

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

class ProbeGroupSettings(Document):
    name = StringField(max_length=120, required=True)
#    probes = ListField(ReferenceField(FunfResource))

