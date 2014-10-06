from django.core.urlresolvers import reverse
from tastypie.bundle import Bundle
from tastypie.resources import Resource
from openpds import getInternalDataStore
from openpds.core.models import Profile

class Document(dict):
    # dictionary-like object for mongodb documents.
    __getattr__ = dict.get

class IDSAnswerResource(Resource):
    def get_internal_datastore(self, request):
        if request and "datastore_owner__uuid" in request.GET and "bearer_token" in request.GET:
            profile, created = Profile.objects.get_or_create(uuid = request.GET["datastore_owner__uuid"])
            token = request.GET["bearer_token"]
            return getInternalDataStore(profile, "", "", token)
        return None

    def get_key(self, request):
        return request.GET["key"] if request is not None and "key" in request.GET else None    
        
    def obj_get_list(self, request=None, **kwargs):
        key = self.get_key(request)
        internalDataStore = self.get_internal_datastore(request)
        # NOTE: maybe check for the type that the value field actually has, rather than relying on this...
        isList = self._meta.isList
        if internalDataStore is None:
            return []
        answer = internalDataStore.getAnswerList(key) if isList else internalDataStore.getAnswer(key)        
        return [Document(d) for d in answer]

    def obj_create(self, bundle, request=None, **kwargs):
        internalDataStore = self.get_internal_datastore(request)
        if internalDataStore is not None and "key" in bundle.data and "value" in bundle.data:
            key = bundle.data["key"]
            value = bundle.data["value"]
            internalDataStore.saveAnswer(key, value)
            bundle.obj = internalDataStore.getAnswerList(key) if self._meta.isList else internalDataStore.getAnswer(key)
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        # The update process is the same as creation - just saving the answer
        return self.obj_create(bundle, request, **kwargs)

    def obj_delete(self, request=None, **kwargs):
        internalDataStore = self.get_internal_datastore(request)
        key = self.get_key(request)
        if internalDataStore is not None and key is not None:
            #NOTE: in the future, we might want to add a way to remove an answer, rather than just nulling it out
            internalDataStore.saveAnswer({ "key": key, "value": [] if self._meta.isList else {}})

    def obj_delete_list(self, request=None, **kwargs):
        # It's ok that this doesn't do anything - we shouldn't be deleting all answers via REST anyway
        pass

    def get_resource_uri(self, item):
        if isinstance(item, Bundle):
            pk = item.obj["key"]
        else:
            pk = item["key"]
        return reverse("api_dispatch_detail", kwargs={
            "resource_name": self._meta.resource_name,
            "api_name": self._meta.api_name, 
            "pk": pk
        })
