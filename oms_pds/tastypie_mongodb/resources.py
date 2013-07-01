from bson import ObjectId
from pymongo import Connection, ASCENDING, DESCENDING

from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.conf import settings

from tastypie.bundle import Bundle
from tastypie.resources import Resource
import pdb

from oms_pds.pds.models import Profile

"""the MONGODB_DATABASE_MULTIPDS setting is set by extract-user-middleware in cases where we need multiple PDS instances within one PDS service """


db = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)
#[settings.MONGODB_DATABASE]


class Document(dict):
    # dictionary-like object for mongodb documents.
    __getattr__ = dict.get

class MongoDBResource(Resource):
    """
    A base resource that allows to make CRUD operations for mongodb.
    """
    def get_collection(self, request):
        """
        Encapsulates collection name.
        """
        try:
            # If no owner is specified in the request, we use the default from settings for now
            # moving forward, we'll want to remove this fallback and require that the owner is specified
            # from the owner uuid, we're looking up the internal identifier from the corresponding profile
            #pdb.set_trace()
            database = settings.MONGODB_DATABASE
            if (request and "datastore_owner__uuid" in request.GET):
                profile, created = Profile.objects.get_or_create(uuid = request.GET["datastore_owner__uuid"])
                database = "User_" + str(profile.uuid).replace("-", "_")
            return db[database][self._meta.collection]
        except AttributeError:
            raise ImproperlyConfigured("Define a collection in your resource.")

    def get_filter_object_value(self, parts, value):
        '''
        Gets object that describes the operation to apply in a filter, as a mongodb filter object. 
        A simple string value means equality. Compound objects are of the form { operation : value }
        For example, "endsin" becomes { "$regex" : "value$" }
        Note: this currently only handles filtering on top-level fields, not sub-fields, etc.
        '''
        # No operator implies equality
        if (len(parts) == 1):
            return value
        
        op = parts[1]
        
        if (op == "endsin"):
            return { "$regex" : value + "$" }
        
        return value

    def get_filter_object(self, request):
        filter_object = {}
        
        if (request == None):
            return filter_object
        
        for var in request.GET:
            if (var not in ["datastore_owner__uuid", "format", "bearer_token", "order_by"]):
                # Ignoring known required querystring parameters, build the filters
                value = request.GET[var]
                parts = var.split("__")
                name = parts[0]
                
                filter_object[name] = self.get_filter_object_value(parts, value)
        
        return filter_object

    def get_order_field_and_direction(self, request):
        if (request is None or "order_by" not in request.GET):
            return None, None
        
        field_name = request.GET["order_by"]
        direction = ASCENDING
        
        if field_name[0] == "-":
            field_name = field_name[1:]
            direction = DESCENDING
        
        return field_name, direction

    def obj_get_list(self, request=None, **kwargs):
        """
        Maps mongodb documents to Document class.
        """
        filter_object = self.get_filter_object(request)
        list = self.get_collection(request).find(filter_object)
        order_field, direction = self.get_order_field_and_direction(request)
        
        if (order_field is not None):
            list.sort(order_field, direction)
        
        return map(Document, list)

    def obj_get(self, request=None, **kwargs):
        """
        Returns mongodb document from provided id.
        """
        return Document(self.get_collection(request).find_one({
            "_id": ObjectId(kwargs.get("pk"))
        }))

    def obj_create(self, bundle, request = None, **kwargs):
        """
        Creates mongodb document from POST data.
        """
        #pdb.set_trace()
        object_id = self.get_collection(request).insert(bundle.data)
        bundle.obj = self.obj_get(request, pk = object_id)
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        """
        Updates mongodb document.
        """
        self.get_collection(request).update({
            "_id": ObjectId(kwargs.get("pk"))
        }, {
            "$set": bundle.data
        })
        return bundle

    def obj_delete(self, request=None, **kwargs):
        """
        Removes single document from collection
        """
        self.get_collection(request).remove({ "_id": ObjectId(kwargs.get("pk")) })

    def obj_delete_list(self, request=None, **kwargs):
        """
        Removes all documents from collection
        """
        self.get_collection(request).remove()

    def get_resource_uri(self, item):
        """
        Returns resource URI for bundle or object.
        """
        if isinstance(item, Bundle):
            pk = item.obj._id
        else:
            pk = item._id
        return reverse("api_dispatch_detail", kwargs={
            "resource_name": self._meta.resource_name,
            "api_name": self._meta.api_name, 
            "pk": pk
        })
