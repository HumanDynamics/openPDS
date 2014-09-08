openPDS - Personal Data Store / Server
======================================

The personal data store component of openPDS handles storage of raw personal data, provides endpoints for writing such data via connectors, a computation engine to perform analysis on the raw data, as well as storage and REST endpoints for results of such analysis (answers to questions, in openPDS lingo).

Please note: openPDS requires a separate registry server for account management and to act as an OAuth 2.0 provider. This can be found at https://github.com/HumanDynamics/openPDS-RegistryServer. If you run your own registry server, your openPDS installation settings.py must be updated to point to your registry server. 

* To get started with openPDS, you must have python pip, virtualenv, and mongodb server installed on your machine:

    >apt-get install python pip
    
    >apt-get install python-virtualenv
    
    >apt-get install mongodb mongodb-server
    
    >service mongodb start

* From there, you can create a virtual environment for your openPDS install, and clone the code into it:

    >virtualenv pdsEnv
    
    >cd pdsEnv
    
    >git clone https://github.com/HumanDynamics/openPDS.git
    
    >source bin/activate
    
    >pip install -r conf/requirements.txt
    
    >python manage.py syncdb
    
    >python manage.py runserver 0.0.0.0:8002 (for access to local VM)
 
* The above steps will start openPDS with default configuration settings on port 8002 of the loopback interface (local access only) on your machine. 
