from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from openpds.core.models import Profile

class Context(models.Model):
        datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="datastore_owner_context")
        context_label = models.CharField(max_length=200)
        context_duration_start = models.CharField(max_length=120, default=False)
        context_duration_end = models.CharField(max_length=120, default=False)
        context_duration_days = models.CharField(max_length=120,default=False)
        context_places = models.TextField(default=False)

        class Meta:
                unique_together = ('datastore_owner', 'context_label')

class Settings(models.Model):
        datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="datastore_owner_settings")
        app_id = models.CharField(max_length=120)
        lab_id = models.CharField(max_length=120)
#        service_id = models.CharField(max_length=120)
#	enabled = models.BooleanField(default=False)
        activity_probe = models.BooleanField(default=False)
        sms_probe = models.BooleanField(default=False)
        call_log_probe = models.BooleanField(default=False)
        bluetooth_probe = models.BooleanField(default=False)
        wifi_probe = models.BooleanField(default=False)
        simple_location_probe = models.BooleanField(default=False)
        screen_probe = models.BooleanField(default=False)
        running_applications_probe = models.BooleanField(default=False)
        hardware_info_probe = models.BooleanField(default=False)
        app_usage_probe = models.BooleanField(default=False)
	context_label = models.ForeignKey(Context, blank = False, null = False, related_name="settings_context_label")

	class Meta:
    		unique_together = ('datastore_owner', 'app_id', 'lab_id')

class Optin(models.Model):
	datastore_owner = models.ForeignKey(Profile, blank = False, null = False, related_name="datastore_owner_optin")
        app_id = models.CharField(max_length=120)
        lab_id = models.CharField(max_length=120)
	data_aggregation = models.BooleanField(default=False)

	class Meta:
                unique_together = ('datastore_owner', 'app_id', 'lab_id')
