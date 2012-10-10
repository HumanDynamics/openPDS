'''
oh no, where is settings.py?!

one of the oms project's universal needs / requirements is that of automation.
we need to automate generating and managing all aspects of app installation and
configuration. to do this for django, we define a configuration schema to use as
our guide to the settings .ini files.

 * compute context variables
 * render settings/local.ini using computed context dict
 * load <project_root>/settings/defaults.ini and settings/local.ini (override
   defaults) - should we include settings/developer.ini too?
'''
import os

from django_configglue.utils import configglue as django_configglue
from oms_deploy.config.schema import OMSDjangoSchema


# XXX - context compute logic goes here
# <repo>/oms_sandbox/settings
#PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')
#MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media')

# XXX render templates w/ context here

# specify configs to read
settings_dir = os.path.abspath(os.path.dirname(__file__))
defaults = os.path.join(settings_dir, 'defaults.ini')
local = os.path.join(settings_dir, 'local.ini')
developer = os.path.join(settings_dir, 'developer.ini')

# make django aware of configglue-based configuration
# this will update django's settings as part of the glue process
# files are read in order as specified here
django_configglue(OMSDjangoSchema, [defaults, local, developer], __name__)
