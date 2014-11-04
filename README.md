openPDS - Personal Data Store / Server
======================================

The personal data store component of openPDS handles storage of raw personal data, provides endpoints for writing such data via connectors, a computation engine to perform analysis on the raw data, as well as storage and REST endpoints for results of such analysis (answers to questions, in openPDS lingo).

Please note: openPDS requires a separate registry server for account management and to act as an OAuth 2.0 provider. This can be found at https://github.com/HumanDynamics/openPDS-RegistryServer. If you run your own registry server, the domain for your registry server must be provided to the openPDS setup script. 

* To get started with openPDS, you must have python pip, virtualenv, and mongodb server installed on your machine:

    >apt-get install python pip
    
    >apt-get install python-virtualenv

    >apt-get install postgresql postgresql-contrib
    
    >apt-get install mongodb mongodb-server

    >apt-get install python-dev libpq-dev
    
    >service mongodb start

* From there, you can create a virtual environment for your openPDS install, and clone the code into it. You must clone the repo into the virtualenv directory for setup.py to work:

    >virtualenv pdsEnv
    
    >cd pdsEnv

    >source bin/activate   

    >git clone https://github.com/HumanDynamics/openPDS.git

    > cd openPDS

    >pip install -r requirements.txt

    >python setup.py

    >python manage.py syncdb
    
    >python manage.py runserver 0.0.0.0:8002 (for access to local VM)
 
* The above steps will start openPDS with default configuration settings on port 8002 of the loopback interface (local access only) on your machine. The openPDS setup script generates a wsgi file that can be used to run openPDS with other web server software, such as Apache. 
