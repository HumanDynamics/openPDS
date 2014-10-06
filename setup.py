#!/usr/bin/env python

import sys
import os


print "NOTE: This must be run from the root directory of the openPDS project"
virtualEnvPath = os.path.dirname(os.getcwd())
virtualEnvPathInput = raw_input("Enter the path to the openPDS virtual environment (or nothing for default: %s): "%virtualEnvPath)
virtualEnvPath = virtualEnvPathInput if virtualEnvPathInput is not None and len(virtualEnvPath) > 0 else virtualEnvPath

registryServer = raw_input("Enter the Registry Server domain name (example: linkedpersonaldata.org): ")

# Create a new wsgi.py file from the template and fill in the virtual env path on it
wsgiTemplateFile = open(os.getcwd() + "/openpds/wsgi.py.template", "r")
wsgiContent = wsgiTemplateFile.read().replace("{{ PATH_TO_OPENPDS_VIRTUALENV }}", virtualEnvPath)
wsgiOutputFile = open(os.getcwd() + "/openpds/wsgi.py", "w")
wsgiOutputFile.write(wsgiContent)
wsgiOutputFile.close()
wsgiTemplateFile.close()

# Determine the backend

backends = { "1": "openpds.backends.mongo", "2": "openpds.backends.sqlite", "3": "openpds.backends.postgres" }

print "Which backend would you like to use for personal data storage?"
print "1. MongoDB (openpds.backends.mongo)"
print "2. SQLite (openpds.backends.sqlite)"
print "3. Postsgres (openpds.backends.postgres)"
selection = raw_input("Enter 1, 2, or 3 (default is 1): ")
selection = "1" if selection is None or len(selection) == 0 else selection

backend = backends[selection]

# Create a new settings.py file from the template and fill in the virtual env / registry server on it
settingsTemplateFile = open(os.getcwd() + "/openpds/settings.py.template", "r")
settingsContent = settingsTemplateFile.read().replace("{{ PATH_TO_OPENPDS_VIRTUALENV }}", virtualEnvPath)
settingsContent = settingsContent.replace("{{ REGISTRY_URL }}", registryServer)
settingsContent = settingsContent.replace("{{ PDS_BACKEND }}", backend)
settingsOutputFile = open(os.getcwd() + "/openpds/settings.py", "w")
settingsOutputFile.write(settingsContent)
settingsTemplateFile.close()
settingsOutputFile.close()

print "wsgi.py and settings.py generated"
print "Setup done. Please continue with django setup by running: ./manage.py syncdb"
print "Make sure that the user running your server process (www-data for apache, for example) has write access to all directories from your PDS virtual env to the openpds package directory"
print "Finally, after running syncdb, provide the user running the server process with write access to the test.db file generated in the openpds directory"
