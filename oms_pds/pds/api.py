from tastypie.authorization import Authorization
from tastypie_mongoengine import resources
from oms_pds.pds.models import Funf, FunfConfig, Role
from oms_pds.authentication import OAuth2Authentication
from oms_pds.authorization import PDSAuthorization
import datetime
import json, ast


class FunfResource(resources.MongoEngineResource):
    class Meta:
        queryset = Funf.objects.all()
        allowed_methods = ('get', 'post')
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization()

    def hydrate(self, bundle):
	#TODO the '.' to '_' translation from the old PDS
        bundle.data['timestamp']=datetime.datetime.fromtimestamp(int(bundle.data['timestamp']))
        return bundle

    def dehydrate(self, bundle):
	# mongoengine is retrieving bundle.data['value'] as a string, and we need to evaluate it as a literal json object
	bundle.data['value'] = ast.literal_eval(bundle.data['value'])
        return bundle

class FunfConfigResource(resources.MongoEngineResource):
    class Meta:
        queryset = FunfConfig.objects.all()
	limit = 1
	ordering = ['-id',]
        allowed_methods = ('get', 'post')
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization()


class RoleResource(resources.MongoEngineResource):
    class Meta:
        queryset = Role.objects.all()
        allowed_methods = ('get', 'post', 'delete')
        authentication = OAuth2Authentication("funf_write")
        authorization = PDSAuthorization()

