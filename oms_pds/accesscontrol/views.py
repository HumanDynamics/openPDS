from django.http import HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms
import datetime
from django.utils import simplejson as json_simple
import os
import sqlite3
import json, ast
from oms_pds import settings
from oms_pds.authorization import PDSAuthorization
from oms_pds.pds.models import Profile
from oms_pds.pds.internal import getInternalDataStore, InternalDataStore
import pdb
from oms_pds.accesscontrol.models import Settings


def funfProbeSettingView(request):
	if request.method=="POST":
		form = FunfProbeSettingForm(request.POST)
      		if form.is_valid():
            		selected = form.cleaned_data.get('selected')
            		#write to model?
    	else:
        	form = FunfProbeSettingForm

    	return render_to_response('funfsettings.html', {'form':form },
        			  context_instance=RequestContext(request))


def storeSettings(request):
	values = {}
	database_columns = ['app_id', 'lab_id', 'service_id', 'enabled', 'activity_probe', 'sms_probe', 'call_log_probe', 'bluetooth_probe', 'wifi_probe', 'simple_location_probe', 'screen_probe', 'running_applications_probe', 'hardware_info_probe', 'app_usage_probe']	
	if request.method == "POST":
		data = json.loads(request.raw_post_data)
		datastore_owner = data.get(u'datastore_owner')
		profile = Profile.objects.get(uuid = datastore_owner)
		for column in database_columns:
			if 'probe' in column or 'enabled' in column:
				values[column] = True if data.get(column) == 1 else False
			else:
				values[column] = data.get(column)
		#settings, created = Settings.objects.get_or_create(datastore_owner = profile, app_id = values['app_id'], lab_id = values['lab_id'], service_id = values['service_id'], enabled = values['enabled'], activity_probe = values['activity_probe'], sms_probe = values['sms_probe'], call_log_probe = values['call_log_probe'], bluetooth_probe = values['bluetooth_probe'], wifi_probe = values['wifi_probe'], simple_location_probe = values['simple_location_probe'], screen_probe = values['screen_probe'], running_applications_probe = values['running_applications_probe'], hardware_info_probe = values['hardware_info_probe'], app_usage_probe = values['app_usage_probe'])
		#settings.save()
		settings, created = Settings.objects.get_or_create(datastore_owner = profile, app_id = values['app_id'], lab_id = values['lab_id'], service_id = values['service_id'])
		settings.enabled = values['enabled']
		settings.activity_probe = values['activity_probe']
		settings.sms_probe = values['sms_probe']
		settings.call_log_probe = values['call_log_probe']
		settings.bluetooth_probe = values['bluetooth_probe']
		settings.wifi_probe = values['wifi_probe']
		settings.simple_location_probe = values['simple_location_probe']
		settings.screen_probe = values['screen_probe']
		settings.running_applications_probe = values['running_applications_probe']
		settings.hardware_info_probe = values['hardware_info_probe']
		settings.app_usage_probe = values['app_usage_probe']
		
		settings.save()
		
	
	return HttpResponse(request.method)

