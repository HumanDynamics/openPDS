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

                        try:
			    context = Context.objects.get(datastore_owner = profile, context_label = data.get('settings_context_label'))
			except Context.DoesNotExist:
			    context = Context.objects.create(datastore_owner = profile, context_label = data.get('settings_context_label'))
			    context.context_duration_start = '10 : 0'
			    context.context_duration_end = '18 : 0'
			    context.context_duration_days = '[0, 1, 1, 1, 1, 1, 0]'
			    context.save()

			#settings, created = Settings.objects.get_or_create(datastore_owner = profile, app_id = values['app_id'], lab_id = values['lab_id'], context_label_id = context.id)

			try:
			    settings = Settings.objects.get(datastore_owner = profile, app_id = values['app_id'], lab_id = values['lab_id'])
			except Settings.DoesNotExist:
			    settings = Settings.objects.create(datastore_owner = profile, app_id = values['app_id'], lab_id = values['lab_id'], context_label_id = context.id)
		        settings.context_label = context
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


def loadAccessControl(request):
    values = {}
    if request.method == "POST":
	data = json.loads(request.raw_post_data)
	datastore_owner = data.get(u'datastore_owner')
	app_id = data.get(u'app_id')
	lab_id = data.get(u'lab_id')

	print(data)
	profile = Profile.objects.get(uuid = datastore_owner)

	settings = []
	try:
	    setting_object = Settings.objects.get(datastore_owner = profile, app_id = app_id, lab_id = lab_id)
	except Settings.DoesNotExist:
	    setting_object = None

	if setting_object is not None:
            setting = {}

	    setting['activity_probe'] = setting_object.activity_probe
	    setting['sms_probe'] = setting_object.sms_probe
            setting['call_log_probe'] = setting_object.call_log_probe
	    setting['bluetooth_probe'] = setting_object.bluetooth_probe
	    setting['wifi_probe'] = setting_object.wifi_probe
	    setting['simple_location_probe'] = setting_object.simple_location_probe
	    setting['screen_probe'] = setting_object.screen_probe
	    setting['running_applications_probe'] = setting_object.running_applications_probe
	    setting['hardware_info_probe'] = setting_object.hardware_info_probe
	    setting['app_usage_probe'] = setting_object.app_usage_probe
	    setting['context_label_id'] = setting_object.context_label_id
            settings.append(setting)

	context_objects = []
	contexts = []
        context_objects = list(Context.objects.all().filter(datastore_owner = profile))

	if len(context_objects) == 0:
	    context = Context.objects.create(datastore_owner = profile, context_label = 'MIT')
            context.context_duration_start = '10 : 0'
            context.context_duration_end = '18 : 0'
            context.context_duration_days = '[0, 1, 1, 1, 1, 1, 0]'
	    context.context_places = ''
            context.save()
	    context_objects.append(context)

	print context_objects
	for context_object in context_objects:
	    context = {}
	    context['id'] = context_object.id
	    print(context_object.id)
	    context['context_label'] = context_object.context_label
	    context['context_duration_start'] = context_object.context_duration_start
	    context['context_duration_end'] = context_object.context_duration_end
	    context['context_duration_days'] = context_object.context_duration_days
	    context['context_places'] = context_object.context_places
	    contexts.append(context)

	return HttpResponse(json.dumps({
        "settings": settings, 
        "contexts": contexts}),
    content_type="application/json")


