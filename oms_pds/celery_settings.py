from celery.schedules import crontab

CELERY_ACKS_LATE = True
CELERYD_PREFETCH_MULTIPLIER = 1

CELERY_IMPORTS = ('oms_pds.tasks',"oms_pds.socialhealth_tasks", "oms_pds.places_tasks", "oms_pds.meetup.tasks", "oms_pds.probedatavisualization_tasks", "oms_pds.mitfit_tasks", "oms_pds.gfsa_tasks", "oms_pds.auth_tasks", "oms_pds.hotspots_tasks")
BROKER_URL = "mongodb://celery:celery@localhost:27017/lpd_celery_broker"
CELERYBEAT_SCHEDULE = {
#    "check-data-and-notify": {
#        "task": "oms_pds.tasks.checkDataAndNotify", 
#        "schedule": crontab(hour="*", minute="0")
#    },
    "compute-social-health-scores": {
        "task": "oms_pds.socialhealth_tasks.recentSocialHealthScores",
        "schedule": crontab(hour="*", minute="0")
     },
    "ensure-funf-indexes": {
        "task": "oms_pds.tasks.ensureFunfIndexes",
        "schedule": crontab(hour="*/2", minute="5")
    },
    "find-recent-places": {
        "task": "oms_pds.places_tasks.findRecentPlaces", 
        "schedule": crontab(hour="*/2", minute="15")
    },
    "find-hourly-places": { 
        "task": "oms_pds.places_tasks.findHourlyPlaces",  
        "schedule": crontab(hour="*/2", minute="20") 
    },
    "probe-summaries": {
        "task": "oms_pds.probedatavisualization_tasks.recentProbeDataScores", 
        "schedule": crontab(hour="*", minute="25")
    },
    "high-active-locations": {
        "task": "oms_pds.mitfit_tasks.findActiveLocationsTask",
        "schedule": crontab(hour="*", minute="30")
    },
    "high-active-times": {
        "task": "oms_pds.mitfit_tasks.findActiveTimesTask",
        "schedule": crontab(hour="*", minute="35")
    },
    "leaderboard-computation": {
        "task": "oms_pds.mitfit_tasks.leaderboardComputationTask",
        "schedule": crontab(hour="*", minute="40")
    },
    "wifi-auth-fingerprints": {
        "task": "oms_pds.auth_tasks.computeAllFingerprints",
        "schedule": crontab(hour="*/2", minute="45")
    },
    "compute-gfsa": {
        "task": "oms_pds.gfsa_tasks.recentGfsaScores",
        "schedule": crontab(hour="*", minute="55")
    },
    "hotspots-computation": {
        "task": "oms_pds.hotspots_tasks.findHotSpotsTask",
        "schedule": crontab(hour="*", minute="30")
    },
}

