"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from oms_pds.accesscontrol.models import FunfProbeGroupSetting, FunfProbeSetting


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

class FunfProbeSettingsTestCase(TestCase):
    def setUp(self):
	#Funf probe groups
	motionGroup = FunfProbeGroupSetting.objects.create(funfProbeGroupName="motion", isProbeGroupSelected=True)
	socialGroup = FunfProbeGroupSetting.objects.create(funfProbeGroupName="social", isProbeGroupSelected=False)	

	#Funf probes
	FunfProbeSetting.objects.create(funfProbe="edu.mit.media.funf.probe.builtin.ActivityProbe", isProbeSelected=True, funfProbeGroup=motionGroup)
	FunfProbeSetting.objects.create(funfProbe="edu.mit.media.funf.probe.builtin.SmsProbe", isProbeSelected=False, funfProbeGroup=socialGroup)

    def testFunfSettings(self):
        """Tests the assignment of probes."""
        activityProbe = FunfProbeSetting.objects.get(funfProbe="edu.mit.media.funf.probe.builtin.ActivityProbe")
        smsProbe = FunfProbeSetting.objects.get(funfProbe="edu.mit.media.funf.probe.builtin.SmsProbe")
        self.assertEqual(activityProbe.getIsProbeSelected(), False) #Should return an assertion error
        self.assertEqual(smsProbe.getIsProbeSelected(), False)
