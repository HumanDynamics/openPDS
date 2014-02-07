from celery.schedules import crontab

CELERY_IMPORTS = ('oms_pds.tasks',"oms_pds.crowdsos_tasks")
BROKER_URL = "mongodb://celery:celery@localhost:27017/crowdsos_celery_broker"
CELERYBEAT_SCHEDULE = {
#    "check-data-and-notify": {
#        "task": "oms_pds.tasks.checkDataAndNotify", 
#        "schedule": crontab(hour="*", minute="0")
#    },
    "ensure-incident-indexes": {
        "task": "oms_pds.crowdsos_tasks.ensureIncidentIndexes",
        "schedule": crontab(hour="*/2", minute="15")
    },
    "find-recent-incidents": {
        "task": "oms_pds.crowdsos_tasks.findRecentIncidents",
        "schedule": crontab(hour="*", minute="*")
    },
    "ensure-funf-indexes": {
        "task": "oms_pds.tasks.ensureFunfIndexes",
        "schedule": crontab(hour="*/2", minute="45")
    }
}

