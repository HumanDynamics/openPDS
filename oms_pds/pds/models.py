from django.db import models
import mongoengine
from tastypie_mongoengine import fields


# Create your models here.

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

