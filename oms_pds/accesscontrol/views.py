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
from oms_pds.accesscontrol.models import Settings, Context

def storeAccessControl(request):
	values = {}
	settings_database_columns = ['app_id', 'lab_id', 'activity_probe', 'sms_probe', 'call_log_probe', 'bluetooth_probe', 'wifi_probe', 'simple_location_probe', 'screen_probe', 'running_applications_probe', 'hardware_info_probe', 'app_usage_probe']	
	context_database_columns = ['context_label', 'context_duration_start', 'context_duration_end', 'context_duration_days', 'context_places']
	if request.method == "POST":
		data = json.loads(request.raw_post_data)
		datastore_owner = data.get(u'datastore_owner')
		profile = Profile.objects.get(uuid = datastore_owner)
	
		if data.get('context_setting_flag') == 0: #context
			context, created = Context.objects.get_or_create(datastore_owner = profile, context_label = data.get('context_label'))
		
			context.context_duration_start = data.get('context_duration_start')
			context.context_duration_end = data.get('context_duration_end')
			context.context_duration_days = data.get('context_duration_days')
			context.context_places = data.get('context_places')
		
			context.save()
		elif data.get('context_setting_flag') == 1: #setting
			for column in settings_database_columns:
				if 'probe' in column:
					values[column] = True if data.get(column) == 1 else False
				else:
					values[column] = data.get(column)

			context = Context.objects.get(datastore_owner = profile, context_label = data.get('settings_context_label'))
			settings, created = Settings.objects.get_or_create(datastore_owner = profile, app_id = values['app_id'], lab_id = values['lab_id'], context_label = context)
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

def deleteAccessControl(request):
	values = {}
	context_database_columns = ['context_label', 'context_duration_start', 'context_duration_end', 'context_duration_days', 'context_places']
        if request.method == "POST":
                data = json.loads(request.raw_post_data)
                datastore_owner = data.get(u'datastore_owner')
                profile = Profile.objects.get(uuid = datastore_owner)

                context = Context.objects.get(datastore_owner = profile, context_label = data.get('context_label'))

                context.delete()

	return HttpResponse(request.method)
