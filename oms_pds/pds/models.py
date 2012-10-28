from django.conf import settings
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

