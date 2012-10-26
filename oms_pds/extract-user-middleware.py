import re
from pymongo import Connection

from django.utils.text import compress_string
from django.utils.cache import patch_vary_headers

from django import http
#import settings
from django.conf import settings
import oms_pds.tastypie_mongodb.resources

class ExtractUser(object):
    """
        This middleware allows multiple pds instances to run on one OMS-PDS service.  It checks the incoming HTTP header request for 'multiPDS_user', if it exists, we create a seperated mongodb instance for the specified user.

	WARNING: The modification of django.conf settings is atypical and used with care.
         
    """
    def process_request(self, request):
        if 'multiPDS_user' in request.GET:
	    print "setting multipds"
##	    db = Connection(
#	        host=getattr(settings, "MONGODB_HOST", None),
#	        port=getattr(settings, "MONGODB_PORT", None)
#	    )["User_"+request.GET['multiPDS_user']]
#	    oms_pds.tastypie_mongodb.resources.Connection = Connection(
#                host=getattr(settings, "MONGODB_HOST", None),
#                port=getattr(settings, "MONGODB_PORT", None)
#            )	["User_"+request.GET['multiPDS_user']]
	    settings.MONGODB_DATABASE_MULTIPDS = "User_"+request.GET['multiPDS_user']

	else:
	    settings.MONGODB_DATABASE_MULTIPDS = None

        return None

