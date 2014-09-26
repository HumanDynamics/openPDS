from celery.schedules import crontab

CELERY_IMPORTS = ('oms_pds.tasks',"oms_pds.socialhealth_tasks", "oms_pds.places_tasks", "oms_pds.meetup.tasks")
BROKER_URL = "mongodb://celery:celery@localhost:27017/celery_broker"
CELERYBEAT_SCHEDULE = {
#    "check-data-and-notify": {
#        "task": "oms_pds.tasks.checkDataAndNotify", 
#        "schedule": crontab(hour="*", minute="0")
#    },
    "compute-social-health-scores": {
        "task": "oms_pds.socialhealth_tasks.recentSocialHealthScores",
        "schedule": crontab(hour="6-23", minute="*/30")
     },
    "smartcatch-notifications": {
        "task": "oms_pds.socialhealth_tasks.smartcatchNotifications",
        "schedule": crontab(hour="*", minute="*/2")
     },
    "ensure-funf-indexes": {
        "task": "oms_pds.tasks.ensureFunfIndexes",
        "schedule": crontab(hour="5-23/2", minute="15")
    },
#    "find-recent-places": {
#        "task": "oms_pds.places_tasks.findRecentPlaces",
#        "schedule": crontab(hour="6-23/2", minute="0")
#    },
#    "schedule-experience-surveys": {
#        "task": "oms_pds.tasks.scheduleExperienceSamplesForToday",
#        "schedule": crontab(hour="9", minute="0")
#    },
    "dump-survey-data": {
        "task": "oms_pds.tasks.dumpSurveyData",
        "schedule": crontab(hour="0", minute="0")
    },
    "dump-funf-data": {
        "task": "oms_pds.tasks.dumpFunfData",
#        "schedule": crontab(hour="*", minute="*")
        "schedule": crontab(hour="0", minute="1")
    },
#    "send-sleep-start-survey": {
#        "task": "oms_pds.tasks.sendSleepStartSurvey",
#       "schedule": crontab(hour="20", minute=0)
#   },
#   "send-sleep-end-survey": {
#       "task": "oms_pds.tasks.sendSleepEndSurvey",
#       "schedule": crontab(hour="5", minute=0)
#   },
    "recent-probe-counts": {
        "task": "oms_pds.tasks.recentProbeCounts",
        "schedule": crontab(hour="*", minute="*")
    },
}

