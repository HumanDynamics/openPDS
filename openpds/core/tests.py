"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase


class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

from openpds.core.internal import SQLiteInternalDataStore, PostgresInternalDataStore
from openpds.core.models import Profile
from openpds.socialhealth_tasks import copyData

def copyDataToPostgres():
    me = Profile.objects.get(id=6)
    sids = SQLiteInternalDataStore(me, "")
    pids = PostgresInternalDataStore(me, "")
    copyData(sids, pids)
    return sids, pids
