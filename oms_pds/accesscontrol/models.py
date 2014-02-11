from django.conf import settings
from django.db import models
from django.utils.translation import gettext as _
from oms_pds.pds.models import Profile

#Funf Settings

class FunfProbeGroupSetting(models.Model):
    funfProbeGroupName = models.CharField(max_length=120)
    isProbeGroupSelected = models.BooleanField(default=False)

class FunfProbeSetting(models.Model):
    funfProbe = models.CharField(max_length=120)
    isProbeSelected = models.BooleanField(default=False)
    funfProbeGroup = models.ForeignKey(FunfProbeGroupSetting)

    def getIsProbeSelected(self):
	return self.isProbeSelected;

class FunfProbeModel(models.Model):
	funfPK = models.CharField(max_length=100,default="funfPK", primary_key=True)
	activityProbe = models.BooleanField(_('Activity'), default=False)
	smsProbe = models.BooleanField(_('SMS'), default=False)
	callLogProbe = models.BooleanField(_('Call Log'), default=False)
	bluetoothProbe = models.BooleanField(_('Bluetooth'), default=False)
	wifiProbe = models.BooleanField(_('Wi-Fi'), default=False)
	simpleLocationProbe = models.BooleanField(_('Simple Location'), default=False)
	screenProbe = models.BooleanField(_('Screen'), default=False) 
	runningApplicationsProbe = models.BooleanField(_('Running Applications'), default=False)


class FunfProbes(models.Model):
	datastoreOwner = models.ForeignKey(Profile, blank = False, null = False, related_name="datastore_owner")
	probesContent = models.TextField()	


#openPDS Settings

