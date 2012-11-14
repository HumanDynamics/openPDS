from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from oms_pds.authentication import OAuth2Authentication
from oms_pds.authorization import PDSAuthorization
from oms_pds.trust.models import SharingLevel, Role, Purpose
import datetime
import json, ast

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from oms_pds.tastypie_mongodb.resources import MongoDBResource, Document


class FunfResource(MongoDBResource):

    id = fields.CharField(attribute="_id")
    title = fields.CharField(attribute="title", null=True, help_text='The funf probe name.')
    time = fields.DateTimeField(attribute="time", null=True, help_text='A human readable datetime.  The time represents when funf collected the data.')
    value = fields.CharField(attribute="value", null=True, help_text='A json blob of funf data.')

    class Meta:
        resource_name = "funf"
        list_allowed_methods = ["delete", "get", "post"]
        authorization = Authorization()
        object_class = Document
        collection = "funf" # collection name

class FunfConfigResource(MongoDBResource):

    id = fields.CharField(attribute="_id")
    key = fields.CharField(attribute="key", null=True)

    class Meta:
        resource_name = "funfconfig"
        list_allowed_methods = ["delete", "get", "post"]
        authorization = Authorization()
        object_class = Document
        collection = "funfconfig" # collection name

class AnswersResource(MongoDBResource):
    id = fields.CharField(attribute="_id", help_text='A guid identifier for an answer entry.')
    key = fields.CharField(attribute="key", help_text='A unique string to identify each answer.', null=False, unique=True)
#    data = fields.ToManyField('oms_pds.pds.api.resources.SocialHealthResource', 'socialhealth_set', related_name='realityanalysis')
    data = fields.DictField(attribute="data", help_text='A json blob of answer data.', null=True, )

    class Meta:
        resource_name = "answers"
        list_allowed_methods = ["delete", "get", "post"]
	help_text='resource help text...'
        authorization = Authorization()
        object_class = Document
        collection = "answers" # collection name

class SharingLevelResource(ModelResource):
    
    class Meta:
	resource_name = 'sharinglevel'
	queryset = SharingLevel.objects.all()

class RoleResource(ModelResource):
    
    class Meta:
	resource_name = 'role'
	queryset = Role.objects.all()

class PurposeResource(ModelResource):
    
    class Meta:
	resource_name = 'purpose'
	queryset = Purpose.objects.all()

