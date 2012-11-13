from django.conf import settings
from django.db import models



class Purpose(models.Model):
    name = models.CharField(max_length=120)
#    author = ReferenceField(User)

class Scope(models.Model):
    name = models.CharField(max_length=120)
    purpose = models.ManyToManyField(Purpose)
    issharing = models.BooleanField(default=False)

class Role(models.Model):
    """ @name : The user defined name of the role
        @purpose : A list of purposes associated with this role
        @tokens : A list of oauth tokens of users assigned to this role """
    name = models.CharField(max_length=120)
    purpose = models.ManyToManyField(Purpose)
    issharing = models.BooleanField(default=False)

class SharingLevel(models.Model):
    level = models.IntegerField()
    purpose = models.ManyToManyField(Purpose)
    isselected = models.BooleanField(default=False)

