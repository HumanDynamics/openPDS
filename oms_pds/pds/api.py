from tastypie.authorization import Authorization
from tastypie_mongoengine import resources
from oms_pds.pds.models import Funf
import datetime
import json, ast


class FunfResource(resources.MongoEngineResource):
    class Meta:
        queryset = Funf.objects.all()
        allowed_methods = ('get', 'post')
        authorization = Authorization()

    def hydrate(self, bundle):
	#TODO the '.' to '_' translation from the old PDS
        bundle.data['timestamp']=datetime.datetime.fromtimestamp(int(bundle.data['timestamp']))
        return bundle

    def dehydrate(self, bundle):
	# mongoengine is retrieving bundle.data['value'] as a string, and we need to evaluate it as a literal json object
	bundle.data['value'] = ast.literal_eval(bundle.data['value'])
        return bundle

