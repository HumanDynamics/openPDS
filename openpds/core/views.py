from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse
from openpds.core.models import Profile
from pymongo import Connection
from openpds import settings
import json

connection = Connection(
    host=getattr(settings, "MONGODB_HOST", None),
    port=getattr(settings, "MONGODB_PORT", None)
)

def dump(request): 
    profiles = Profile.objects.all()
    data = {}

    for profile in profiles:
        db = connection["User_" + str(profile.id)]
        funf = db["funf"]
        data[profile.uuid] = funf.find()

    return render_to_response("dataDump.csv", data)
