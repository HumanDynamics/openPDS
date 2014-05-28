from django.http import HttpResponse, HttpResponseBadRequest
from django.template import RequestContext
from django.shortcuts import render_to_response
from django import forms
import datetime
from django.utils import simplejson as json_simple
import os
import sqlite3
import json, ast
from openpds import settings
from openpds.authorization import PDSAuthorization
from openpds.core.models import Profile
from openpds.backends.mongo import getInternalDataStore, InternalDataStore
import pdb
from openpds.accesscontrol.models import Settings, Context, Optin

def storeAccessControl(request):
    values = {}
    settings_database_columns = ['app_id', 'lab_id', 'activity_probe', 'sms_probe', 'call_log_probe', 'bluetooth_probe', 'wifi_probe', 'simple_location_probe', 'screen_probe', 'running_applications_probe', 'hardware_info_probe', 'app_usage_probe']	
    context_database_columns = ['context_label', 'context_duration_start', 'context_duration_end', 'context_duration_days', 'context_places']
    if request.method == "POST":
        data = json.loads(request.raw_post_data)

        datastore_owner = data.get(u'datastore_owner')

	data_aggregation = data.get(u'data_aggregation')
	app_id = data.get(u'app_id')
	lab_id = data.get(u'lab_id')

	profile = Profile.objects.get(uuid = datastore_owner)
	
	print profile
	print app_id
	print lab_id
	optin, created = Optin.objects.get_or_create(datastore_owner = profile, app_id = app_id, lab_id = lab_id)
	optin.app_id = app_id
	optin.lab_id = lab_id
	optin.data_aggregation = data_aggregation
	optin.save()

	context_object = data.get('context_object')
	if context_object:
	    context, created = Context.objects.get_or_create(datastore_owner = profile, context_label = context_object['context_label'])
		
	    print context_object.keys()
	    context.context_duration_start = context_object['context_duration_start']
	    context.context_duration_end = context_object['context_duration_end']
	    context.context_duration_days = context_object['context_duration_days']
	    context.context_places = context_object['context_places']
		
	    context.save()

	setting_object = data.get('setting_object')
	print "setting object is:"
	print setting_object
	if setting_object:
	    for column in settings_database_columns:
	        if column in setting_object:
		    if 'probe' in column:
		        values[column] = True if setting_object[column] == 1 else False
		    else:
			values[column] = setting_object[column]
		else: #extraneous probes
		    values[column] = False
	    print values

            try:
		context = Context.objects.get(datastore_owner = profile, context_label = setting_object['settings_context_label'])
	    except Context.DoesNotExist:
		context = Context.objects.create(datastore_owner = profile, context_label = setting_object['settings_context_label'])
		context.context_duration_start = '10 : 0'
		context.context_duration_end = '18 : 0'
		context.context_duration_days = '[0, 1, 1, 1, 1, 1, 0]'
	        context.save()

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

	context_object = data.get('context_object')
        context = Context.objects.get(datastore_owner = profile, context_label = context_object['context_label'])

        context.delete()

    return HttpResponse(request.method)


def loadAccessControl(request):
    values = {}
    if request.method == "POST":
	data = json.loads(request.raw_post_data)
	datastore_owner = data.get(u'datastore_owner')
	app_id = data.get(u'app_id')
	lab_id = data.get(u'lab_id')

	profile = Profile.objects.get(uuid = datastore_owner)

	probes = {'activity_probe': False, 'sms_probe': False, 'call_log_probe': False, 
            	  'bluetooth_probe': False, 'wifi_probe': False, 'simple_location_probe': False,
                  'screen_probe': False, 'running_applications_probe': False, 
		  'hardware_info_probe': False, 'app_usage_probe': False}

	for probe_object in Settings.objects.filter(datastore_owner = profile):
	    probes['activity_probe'] = probes['activity_probe'] or probe_object.activity_probe
	    probes['sms_probe'] = probes['sms_probe'] or probe_object.sms_probe
	    probes['call_log_probe'] = probes['call_log_probe'] or probe_object.call_log_probe
	    probes['bluetooth_probe'] = probes['bluetooth_probe'] or probe_object.bluetooth_probe
	    probes['wifi_probe'] = probes['wifi_probe'] or probe_object.wifi_probe
	    probes['simple_location_probe'] = probes['simple_location_probe'] or probe_object.simple_location_probe
	    probes['screen_probe'] = probes['screen_probe'] or probe_object.screen_probe
	    probes['running_applications_probe'] = probes['running_applications_probe'] or probe_object.running_applications_probe
	    probes['hardware_info_probe'] = probes['hardware_info_probe'] or probe_object.hardware_info_probe
	    probes['app_usage_probe'] = probes['app_usage_probe'] or probe_object.app_usage_probe
	    print probes
	
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
	    context.context_places = '[lat/lng: (42.3591326,-71.093201)]'
            context.save()
	    context_objects.append(context)

            context = Context.objects.create(datastore_owner = profile, context_label = 'Alltime-Everywhere')
            context.context_duration_start = '0 : 0'
            context.context_duration_end = '23 : 59'
            context.context_duration_days = '[1, 1, 1, 1, 1, 1, 1]'
            context.context_places = ''
            context.save()
            context_objects.append(context)

	for context_object in context_objects:
	    context = {}
	    context['id'] = context_object.id
	    context['context_label'] = context_object.context_label
	    context['context_duration_start'] = context_object.context_duration_start
	    context['context_duration_end'] = context_object.context_duration_end
	    context['context_duration_days'] = context_object.context_duration_days
	    context['context_places'] = context_object.context_places
	    contexts.append(context)

	data_aggregation = False
        try:
            optin_object = Optin.objects.get(datastore_owner = profile, app_id = app_id, lab_id = lab_id)
        except Optin.DoesNotExist:
            optin_object = None
	
	if optin_object:
	    data_aggregation = optin_object.data_aggregation

	return HttpResponse(json.dumps({
        "settings": settings, 
        "contexts": contexts,
	"probes": probes,
	"data_aggregation": data_aggregation}),
    content_type="application/json")


def loadProbes(request):
    values = {}
    if request.method == "POST":
        data = json.loads(request.raw_post_data)
        datastore_owner = data.get(u'datastore_owner')
        profile = Profile.objects.get(uuid = datastore_owner)

        probes = {'activity_probe': False, 'sms_probe': False, 'call_log_probe': False,
                  'bluetooth_probe': False, 'wifi_probe': False, 'simple_location_probe': False,
                  'screen_probe': False, 'running_applications_probe': False,
                  'hardware_info_probe': False, 'app_usage_probe': False}

        for probe_object in Settings.objects.all():
            probes['activity_probe'] = probes['activity_probe'] or probe_object.activity_probe
            probes['sms_probe'] = probes['sms_probe'] or probe_object.sms_probe
            probes['call_log_probe'] = probes['call_log_probe'] or probe_object.call_log_probe
            probes['bluetooth_probe'] = probes['bluetooth_probe'] or probe_object.bluetooth_probe
            probes['wifi_probe'] = probes['wifi_probe'] or probe_object.wifi_probe
            probes['simple_location_probe'] = probes['simple_location_probe'] or probe_object.simple_location_probe
            probes['screen_probe'] = probes['screen_probe'] or probe_object.screen_probe
            probes['running_applications_probe'] = probes['running_applications_probe'] or probe_object.running_applications_probe
            probes['hardware_info_probe'] = probes['hardware_info_probe'] or probe_object.hardware_info_probe
            probes['app_usage_probe'] = probes['app_usage_probe'] or probe_object.app_usage_probe

        return HttpResponse(json.dumps({
            "probes": probes}),
            content_type="application/json")

def globalAccessControl(request):
    values = {}
    if request.method == "POST":
        data = json.loads(request.raw_post_data)
        datastore_owner = data.get(u'datastore_owner')
	probes = data.get(u'probes')
        profile = Profile.objects.get(uuid = datastore_owner)
	
	settingsCollection = list(Settings.objects.filter(datastore_owner = profile))
	for setting in settingsCollection:
	    setting.activity_probe = probes.get(u'activity_probe')
            setting.sms_probe = probes.get(u'sms_probe')
            setting.call_log_probe = probes.get(u'call_log_probe')
            setting.bluetooth_probe = probes.get(u'bluetooth_probe')
            setting.wifi_probe = probes.get(u'wifi_probe')
            setting.simple_location_probe = probes.get(u'simple_location_probe')
            setting.screen_probe = probes.get(u'screen_probe')
            setting.running_applications_probe = probes.get(u'running_applications_probe')
            setting.hardware_info_probe = probes.get(u'hardware_info_probe')
            setting.app_usage_probe = probes.get(u'app_usage_probe')
	    
	    setting.save()

    return HttpResponse(request.method)
