from tastypie.authorization import Authorization
from tastypie.resources import ModelResource
from oms_pds.authentication import OAuth2Authentication
from oms_pds.authorization import PDSAuthorization
import datetime
import json, ast

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from oms_pds.tastypie_mongodb.resources import MongoDBResource, Document
from oms_pds.pds.models import Purpose

class FunfResource(MongoDBResource):

    id = fields.CharField(attribute="_id")
    title = fields.CharField(attribute="title", null=True)
    time = fields.DateTimeField(attribute="time", null=True)
    value = fields.CharField(attribute="value", null=True)

    class Meta:
        authentication = OAuth2Authentication("reality_analysis")
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


class RealityAnalysisResource(MongoDBResource):
    id = fields.CharField(attribute="_id")
    key = fields.CharField(attribute="key", help_text='A unique string identifier', null=False, unique=True)
#    data = fields.ToManyField('oms_pds.pds.api.resources.SocialHealthResource', 'socialhealth_set', related_name='realityanalysis')
    data = fields.ListField(attribute="data", null=True, )

    class Meta:
        resource_name = "realityanalysis"
        list_allowed_methods = ["delete", "get", "post"]
        authorization = Authorization()
        object_class = Document
        collection = "realityanalysis" # collection name

    
class SocialHealthResource(MongoDBResource):
    layer = fields.CharField(attribute="layer", null=False)
    value = fields.CharField(attribute="value", null=False)
    key = fields.CharField(attribute="key", null=False)
    
    class Meta:
        resource_name = "socialhealth"
        list_allowed_methods = ["delete", "get", "post"]
        authorization = Authorization()
        object_class = Document
        collection = "socialhealth" # collection name


class RoleResource(MongoDBResource):

    id = fields.CharField(attribute="_id")
    key = fields.CharField(attribute="key", null=True)
    ids = fields.ListField(attribute="ids", null=True)

    class Meta:
        resource_name = "role"
        list_allowed_methods = ["delete", "get", "post"]
        authorization = Authorization()
        object_class = Document
        collection = "role" # collection name


class PurposeResource(MongoDBResource):
    key = fields.CharField(attribute="key", help_text='A unique string identifier', null=False, unique=True)
    sharinglevels = fields.ToManyField('oms_pds.pds.api.resources.SharingLevelResource', 'sharinglevel_set', related_name='purpose')
    roles = fields.ToManyField('oms_pds.pds.api.resources.RoleResource', 'role_set', related_name='purpose')
    scopes = fields.ToManyField('oms_pds.pds.api.resources.ScopeResource', 'scope_set', related_name='purpose')

    class Meta:
        resource_name = 'purpose'
        list_allowed_methods = ["delete", "get", "post"]
        authorization = Authorization()
        object_class = Document
        collection = "purpose" # collection name

class RoleResource(MongoDBResource):
    purpose = fields.ToManyField(PurposeResource, 'purpose')
    key = fields.CharField(attribute="key", null=False, unique=True)

    class Meta:
        resource_name = 'role'
        list_allowed_methods = ["delete", "get", "post"]
        authorization = Authorization()
        object_class = Document
        collection = "role" # collection name

class ScopeResource(MongoDBResource):
    purpose = fields.ToManyField(PurposeResource, 'purpose')
    key = fields.CharField(attribute="key", null=False, unique=True)

    class Meta:
        resource_name = 'scope'
        list_allowed_methods = ["delete", "get", "post"]
        authorization = Authorization()
        object_class = Document
        collection = "scope" # collection name

class SharingLevelResource(MongoDBResource):
    purpose = fields.ToManyField(PurposeResource, 'purpose')
    key = fields.CharField(attribute="key", null=False, unique=True)

    class Meta:
        resource_name = 'sharinglevel'
        list_allowed_methods = ["delete", "get", "post"]
        authorization = Authorization()
        object_class = Document
        collection = "sharinglevel" # collection name

