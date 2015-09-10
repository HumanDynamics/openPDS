from celery.schedules import crontab

CELERY_IMPORTS = ('oms_pds.tasks',"oms_pds.socialhealth_tasks", "oms_pds.places_tasks", "oms_pds.meetup.tasks")
BROKER_URL = "mongodb://celery:celery@localhost:27017/celery_broker"
CELERYBEAT_SCHEDULE = {
#    "check-data-and-notify": {
#        "task": "oms_pds.tasks.checkDataAndNotify", 
#        "schedule": crontab(hour="*", minute="0")
#    },
    "compute-social-health-scores": { #computation of weekly social health scores
        "task": "oms_pds.socialhealth_tasks.recentSocialHealthScores2",
        #"schedule": crontab(hour="*/4", minute="0")
        "schedule": crontab(hour="*", minute="*/14")
     },
    "compute-survey-scores": { #computation of weekly survey scores
        "task": "oms_pds.socialhealth_tasks.recentSurveyScores",
        #"schedule": crontab(hour="*/6", minute="0")
        "schedule": crontab(hour="*", minute="*/15")
     },
    "compute-hourly-social-health-scores": { #computation of hourly social health scores for historical view
        "task": "oms_pds.socialhealth_tasks.hourlySocialHealthScores",
        #"schedule": crontab(hour="*", minute="*/50")
        "schedule": crontab(hour="*", minute="*/16")
     },
    "compute-daily-survey-scores": { #computation of daily survey scores for historical view
        "task": "oms_pds.socialhealth_tasks.dailySurveyScores",
        #"schedule": crontab(hour="*/11", minute="0")
        "schedule": crontab(hour="*", minute="*/17")
        #"schedule": crontab(hour="*", minute="*")
     },
    "determine-avgs-and-history-social-health-scores": { #update history for social health and surveys. Also calculate averages for each user
        "task": "oms_pds.socialhealth_tasks.saveHistory",
        #"schedule": crontab(hour="*", minute="*/45")
        "schedule": crontab(hour="*/4", minute="0")
        #"schedule": crontab(hour="*", minute="*")
     },
    "smartcatch-notifications": {
        "task": "oms_pds.socialhealth_tasks.smartcatchNotifications",
        "schedule": crontab(hour="*", minute="*/15")
        #"schedule": crontab(hour="*", minute="*")
     },
    "ensure-funf-indexes": {
        "task": "oms_pds.tasks.ensureFunfIndexes",
#        "schedule": crontab(hour="5-23/2", minute="15")
        "schedule": crontab(hour="*", minute="*/25")
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
        "schedule": crontab(hour="*", minute="*/20")
    },
    "dump-funf-data": {
        "task": "oms_pds.tasks.dumpFunfData",
        "schedule": crontab(hour="*", minute="*/15")
#        "schedule": crontab(hour="0", minute="1")
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
        "schedule": crontab(hour="*", minute="*/15")
    },
}

