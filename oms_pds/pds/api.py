from tastypie.authorization import Authorization
from tastypie.resources import ModelResource, fields, ALL_WITH_RELATIONS
from oms_pds.authentication import OAuth2Authentication
from oms_pds.authorization import PDSAuthorization
#from oms_pds.trust.models import SharingLevel, Role, Purpose
from oms_pds import settings
import datetime
import json, ast

from tastypie import fields
from tastypie.authorization import Authorization
from tastypie.validation import Validation
from oms_pds.tastypie_mongodb.resources import MongoDBResource, Document
from oms_pds.pds.models import AuditEntry, Profile, SharingLevel, Role, Purpose, Scope
from django.db import models

import pdb

class FunfResource(MongoDBResource):

    id = fields.CharField(attribute="_id")
    key = fields.CharField(attribute="key", null=True, help_text='The funf probe name.')
    time = fields.DateTimeField(attribute="time", null=True, help_text='A human readable datetime.  The time represents when funf collected the data.')
    value = fields.CharField(attribute="value", null=True, help_text='A json blob of funf data.')

    class Meta:
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = True)
        resource_name = "funf"
        list_allowed_methods = ["delete", "get", "post"]
#        authorization = Authorization()
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

class AnswerResource(MongoDBResource):
    id = fields.CharField(attribute="_id", help_text='A guid identifier for an answer entry.')
    key = fields.CharField(attribute="key", help_text='A unique string to identify each answer.', null=False, unique=True)
#    data = fields.ToManyField('oms_pds.pds.api.resources.SocialHealthResource', 'socialhealth_set', related_name='realityanalysis')
    value = fields.DictField(attribute="data", help_text='A json blob of answer data.', null=True, )

    class Meta:
        resource_name = "answer"
        list_allowed_methods = ["delete", "get", "post"]
	help_text='resource help text...'
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = True)
        object_class = Document
        collection = "answer" # collection name

class AnswerListResource(MongoDBResource):
    id = fields.CharField(attribute="_id", help_text='A guid identifier for an answer entry.')
    key = fields.CharField(attribute="key", help_text='A unique string to identify each answer.', null=False, unique=True)
#    data = fields.ToManyField('oms_pds.pds.api.resources.SocialHealthResource', 'socialhealth_set', related_name='realityanalysis')
    value = fields.ListField(attribute="data", help_text='A list json blob of answer data.', null=True, )

    class Meta:
        resource_name = "answerlist"
        list_allowed_methods = ["delete", "get", "post"]
	help_text='resource help text...'
        authorization = Authorization()
        object_class = Document
        collection = "answerlist" # collection name

class SharingLevelResource(ModelResource):
    
    class Meta:
	queryset = SharingLevel.objects.all()
	resource_name = 'sharinglevel'
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = True)
        filtering = { "datastore_owner_id": ["contains"]}

    def get_object_list(self, request):
        return super(SharingLevelResource, self).get_object_list(request).filter(datastore_owner_id=request.GET.get('datastore_owner'))

    def hydrate(self, bundle):
	bundle.obj.datastore_owner_id = str(bundle.request.GET.get('datastore_owner'))
	return bundle

class RoleResource(ModelResource):
    
    class Meta:
	resource_name = 'role'
	queryset = Role.objects.all()
        list_allowed_methods = ["delete", "get", "post"]
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = True)

    def get_object_list(self, request):
        return super(RoleResource, self).get_object_list(request).filter(datastore_owner_id=request.GET.get('datastore_owner'))

    def hydrate(self, bundle):
	bundle.obj.datastore_owner_id = str(bundle.request.GET.get('datastore_owner'))
	return bundle

class PurposeResource(ModelResource):
    
    class Meta:
	resource_name = 'purpose'
        queryset = Purpose.objects.all()
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = True)
        filtering = { "uuid": ["contains"]}

    def get_object_list(self, request):
        return super(PurposeResource, self).get_object_list(request).filter(datastore_owner_id=request.GET.get('datastore_owner'))

    def hydrate(self, bundle):
	bundle.obj.datastore_owner_id = str(bundle.request.GET.get('datastore_owner'))
	return bundle

class ScopeResource(ModelResource):

    class Meta:
        resource_name = 'scope'
        queryset = Scope.objects.all()
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = True)

    def get_object_list(self, request):
        return super(ScopeResource, self).get_object_list(request).filter(datastore_owner_id=request.GET.get('datastore_owner'))

    def hydrate(self, bundle):
	bundle.obj.datastore_owner_id = str(bundle.request.GET.get('datastore_owner'))
	return bundle

class ProfileResource(ModelResource):
    
    class Meta:
        queryset = Profile.objects.all()
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = True)
        filtering = { "uuid": ["contains"]}

class AuditEntryCountResource(ModelResource):
    def get_resource_uri(self, bundle): 
        # Returning nothing here... there isn't a model backing this resource, so there's nowhere to pull this from
        return ""
    
    def dehydrate(self, bundle):
        # Since there's no backing model here, tastypie for some reason doesn't fill in the necessary fields on the data
        # As a result, this must be done manually
        bundle.data['date'] = bundle.obj['date']
        bundle.data['count'] = bundle.obj['count']
        return bundle
    
    def build_filters(self, filters):
        applicable_filters = super(AuditEntryCountResource, self).build_filters(filters)
        
        qset = None
        date_gte = filters.get("date__gte")
        
        if (date_gte):            
            qset = models.Q(timestamp__gte = date_gte + " 00:00:00Z")
        
        date_lte = filters.get("date__lte")
        
        if (date_lte):
            qset2 = (models.Q(timestamp__lte = date_lte + " 23:59:59Z"))
            qset = qset & qset2 if qset else qset2
        
        if (qset):
            applicable_filters["time_filter"] = qset
        
        return applicable_filters
    
    def apply_filters(self, request, applicable_filters):
        time_filter = None
        
        if ("time_filter" in applicable_filters):
            time_filter= applicable_filters.pop("time_filter")
        
        semi_filtered = super(AuditEntryCountResource, self).apply_filters(request, applicable_filters)
        
        return semi_filtered.filter(time_filter) if time_filter else semi_filtered

    class Meta:
        queryset = AuditEntry.objects.extra({ 'date' : 'date(timestamp)'}).values('date').annotate(count = models.Count("id"))
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = False)
        fields = ['date', 'count']
        allowed_methods = ('get')
        filtering = { "date" : ["gte", "lte", "gt", "lt"]}
        ordering = ("date");

class AuditEntryResource(ModelResource):
    datastore_owner = fields.ForeignKey(ProfileResource, 'datastore_owner', full = True)
    requester = fields.ForeignKey(ProfileResource, 'requester', full = True)
    
    def dehydrate(self, bundle):
        bundle.data['timestamp_date'] = bundle.data['timestamp'].date()
        bundle.data['timestamp_time'] = bundle.data['timestamp'].time().strftime('%I:%M:%S %p')
        return bundle
    
    class Meta:
        queryset = AuditEntry.objects.all()
        # POST is provided to allow a Resource or Sandbox server to store audit entries on the PDS
        allowed_methods = ('get', 'post')
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization(scope = "funf_write", audit_enabled = False)
        filtering = { "datastore_owner" : ["exact"],
                      "timestamp": ["gte", "lte", "gt", "lt"],
                      "script": ["contains"], 
                      "requester": ALL_WITH_RELATIONS }
        ordering = ('timestamp')
        limit = 20


