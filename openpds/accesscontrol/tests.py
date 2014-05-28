"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
#from oms_pds.accesscontrol.models import FunfProbeGroupSetting, FunfProbeSetting
from oms_pds.pds.internal import getAccessControlledInternalDataStore
import sqlite3
from oms_pds.pds.models import Profile
from oms_pds.pds.internal import getInternalDataStore, InternalDataStore
from oms_pds.accesscontrol.models import Settings

from oms_pds.probedatavisualization_tasks import recentProbeDataScores 
class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

#class FunfProbeSettingsTestCase(TestCase):
#    def setUp(self):
#	#Funf probe groups
#	motionGroup = FunfProbeGroupSetting.objects.create(funfProbeGroupName="motion", isProbeGroupSelected=True)
#	socialGroup = FunfProbeGroupSetting.objects.create(funfProbeGroupName="social", isProbeGroupSelected=False)	
#
#	#Funf probes
#	FunfProbeSetting.objects.create(funfProbe="edu.mit.media.funf.probe.builtin.ActivityProbe", isProbeSelected=True, funfProbeGroup=motionGroup)
#	FunfProbeSetting.objects.create(funfProbe="edu.mit.media.funf.probe.builtin.SmsProbe", isProbeSelected=False, funfProbeGroup=socialGroup)
#
#    def testFunfSettings(self):
#        """Tests the assignment of probes."""
#        activityProbe = FunfProbeSetting.objects.get(funfProbe="edu.mit.media.funf.probe.builtin.ActivityProbe")
#        smsProbe = FunfProbeSetting.objects.get(funfProbe="edu.mit.media.funf.probe.builtin.SmsProbe")
#        self.assertEqual(activityProbe.getIsProbeSelected(), False) #Should return an assertion error
#        self.assertEqual(smsProbe.getIsProbeSelected(), False)

class InternalDataStoreTest(TestCase):
	def setUp(self):
		#user
		owner = Profile.objects.create(uuid='12345')
		access_control_setting = Settings.objects.create(datastore_owner_id = owner.id, app_id = 'app', lab_id = 'lab', service_id = 'service', enabled = 0, activity_probe = 1, sms_probe = 1, call_log_probe = 1, bluetooth_probe = 1, wifi_probe = 1, simple_location_probe = 1, screen_probe = 1, running_applications_probe = 1, hardware_info_probe = 1, app_usage_probe = 1)  

	def test_creation(self):
		try:
			owner = Profile.objects.get(uuid='12345')
			internalDataStore = getAccessControlledInternalDataStore(owner, "app", "lab", "service")
			internalDataStore.getData('bluetooth_probe', 0, 1000)
		except Profile.DoesNotExist:
			print "Does not exist"

class ProbeDataVisualizationTest(TestCase):
	def test_visualization(self):
		recentProbeDataScores()
