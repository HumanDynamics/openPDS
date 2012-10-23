from tastypie.authorization import Authorization
from tastypie_mongoengine import resources
from oms_pds.authentication import OAuth2Authentication
from oms_pds.authorization import PDSAuthorization
import datetime
import json, ast

from tastypie import fields
from tastypie.authorization import Authorization

from oms_pds.tastypie_mongodb.resources import MongoDBResource, Document

class FunfResource(MongoDBResource):

    id = fields.CharField(attribute="_id")
    title = fields.CharField(attribute="title", null=True)
    time = fields.DateTimeField(attribute="time", null=True)
    value = fields.CharField(attribute="value", null=True)

    class Meta:
        resource_name = "funf"
        list_allowed_methods = ["delete", "get", "post"]
        authorization = Authorization()
        object_class = Document
        collection = "funf" # collection name
