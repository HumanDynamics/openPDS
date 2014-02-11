# Django settings for OMS_PDS project.

import os

DEBUG = False
TEMPLATE_DEBUG = DEBUG
MONGODB_HOST = None
MONGODB_PORT = None
MONGODB_DATABASE = 'pds'
SERVER_OMS_REGISTRY='linkedpersonaldata.org'
USE_MULTIPDS = True
SERVER_UPLOAD_DIR="/var/www/trustframework/pdsEnv/"

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/var/www/trustframework/pdsEnv/OMS-PDS/oms_pds/test.db',                      # Or path to database file if using sqlite3.
        #'NAME': 'test.db',
        'USER': 'test',                      # Not used with sqlite3.
        'PASSWORD': 'test',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(os.path.dirname(__file__), 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r6ce2%&xce!o!t9$i(#2rxr)=49a_u8@pwiye^ug6f82#5qa!!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'oms_pds.django-crossdomainxhr-middleware.XsSharing',
    'oms_pds.extract-user-middleware.ExtractUser',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'oms_pds.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'oms_pds.apache.django.application'

TEMPLATE_DIRS = (os.path.join(os.path.dirname(__file__), 'templates'),)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'oms_pds.pds',
    'oms_pds.sharing',
    'oms_pds.trust',
    'djcelery',
    #'oms_pds.ra_celery',
    'kombu.transport.django',
    'oms_pds.visualization',
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'oms_pds.accesscontrol',
)

#django celery configuration

from celery.schedules import crontab

CELERY_IMPORTS = ('oms_pds.tasks','oms_pds.socialhealth_tasks')
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


import djcelery

djcelery.setup_loader()



# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
	'logfile': {
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': '/var/www/trustframework/pdsEnv/OMS-PDS/log/error.log',
	    'formatter': 'verbose'
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
	'django': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
        'oms_pds': {
            'handlers':['logfile'],
            'propagate': True,
            'level':'DEBUG',
        },
    }
}

GCM_API_KEY = "AIzaSyBUTRwrWhHeV8qU-ySAHTG11YyrqcThSLI"
