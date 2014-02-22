from celery.schedules import crontab

CELERY_IMPORTS = ('oms_pds.tasks',"oms_pds.socialhealth_tasks")
BROKER_URL = "mongodb://celery:celery@localhost:27017/lpd_celery_broker"
CELERYBEAT_SCHEDULE = {
#    "check-data-and-notify": {
#        "task": "oms_pds.tasks.checkDataAndNotify", 
#        "schedule": crontab(hour="*", minute="0")
#    },
    "compute-social-health-scores": {
        "task": "oms_pds.socialhealth_tasks.recentSocialHealthScores",
        "schedule": crontab(hour="*", minute="*/30")
     },
    "ensure-funf-indexes": {
        "task": "oms_pds.tasks.ensureFunfIndexes",
        "schedule": crontab(hour="*/2", minute="15")
    },
    "find-recent-places": {
        "task": "oms_pds.tasks.findRecentPlaces", 
        "schedule": crontab(hour="*/2", minute="0")
    }
}

