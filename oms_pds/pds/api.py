from tastypie.authorization import Authorization
from tastypie_mongoengine import resources
from oms_pds.pds.models import Funf
import datetime
import json


class FunfResource(resources.MongoEngineResource):
    class Meta:
        queryset = Funf.objects.all()
        allowed_methods = ('get', 'post')
        authorization = Authorization()

    def hydrate(self, bundle):
	print bundle.data['value']
        bundle.data['timestamp']=datetime.datetime.fromtimestamp(int(bundle.data['timestamp']))
        return bundle

    def dehydrate(self, bundle):
#        ustr_to_load = unicode(bundle.data['value'], 'latin-1')
#        jvalue=json.loads(bundle.data['value'])
#	print bundle.data['value']
 #       bundle.data['value']=jvalue
        return bundle

