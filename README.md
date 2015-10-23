openPDS - Personal Data Store / Server
======================================

The personal data store component of [openPDS](http://openpds.media.mit.edu/) handles storage of raw personal data, provides endpoints for writing such data via connectors, a computation engine to perform analysis on the raw data, as well as storage and REST endpoints for results of such analysis (answers to questions, in openPDS lingo).

__Please note__: openPDS requires a separate registry server for account management and to act as an OAuth 2.0 provider. This can be found at https://github.com/HumanDynamics/openPDS-RegistryServer. If you run your own registry server, the domain for your registry server must be provided to the openPDS setup script. 

__Contributors__: The dev branch is for ongoing development. Please submit pull requests to this brach.

## Getting started with openPDS
(You must have python pip, virtualenv, and mongodb server installed on your machine)

```sh
# install python and database dependencies
apt-get install python pip
apt-get install python-virtualenv
apt-get install postgresql postgresql-contrib
apt-get install mongodb mongodb-server
apt-get install python-dev libpq-dev

service mongodb start
```

## Creating a [python virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for openPDS
You must clone the repo into the virtualenv directory for `setup.py` to work:

```sh
# create the virtual environment
virtualenv pdsEnv
cd pdsEnv
source bin/activate   

# get the latest openPDS code
git clone https://github.com/HumanDynamics/openPDS.git
cd openPDS

# install openPDS and its requirements
pip install -r requirements.txt

# set up and run your local openPDS
python start.py
python manage.py syncdb
python manage.py runserver 0.0.0.0:8002 (for access to local VM)
```
 
 The above steps will start openPDS with default configuration settings on port `8002` of the loopback interface (local access only) on your machine. The openPDS setup script generates a wsgi file that can be used to run openPDS with other web server software, such as Apache. 
