from django.db import models
from tastypie_mongoengine import fields
import mongoengine

class Funf(mongoengine.Document):
    name = mongoengine.StringField()
    timestamp = mongoengine.DateTimeField()
    value = mongoengine.DynamicField()

    def __unicode__(self):
        return self.name

class FunfConfig(mongoengine.Document):
    key = mongoengine.StringField()


class Role(mongoengine.Document):
    key = mongoengine.StringField()
    ids = mongoengine.ListField(mongoengine.IntField())

    def __unicode__(self):
        return self.key

