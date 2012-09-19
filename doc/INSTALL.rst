OMS PDS INSTALL
===============

NOTES
-----

*this is a work in progress and will see updates and improvement - please feel free to submit your feedback to make this a better experience for you*

*some level of console experience and comfort is expected, though we have done our best to take out the pain in deploying this application :)*

in the future, this web app will be remotely deployable - eg, developers and system admins will have the tools to deploy this application to a remote server, from a local copy of the git repo. for now the installation scripts only support being run locally.


requirements / expectations
---------------------------

* upload a copy of the git repository to the server
* a user with access to root priviledges via sudo 
* root password has been set, and you know it
* you have access to a github account with access to the ResourceServer repository
* a ubuntu 12.04 LTS server
* openssh, apache, mongodb, and mysql setup and running


steps to install the resource server
------------------------------------

* run ``fab create_config`` from within this repo and answer the questions you are presented with
* run ``fab deploy_project``, also from within the repo, and watch oms_fabric deploy the resource server for you. you will need to provide your github username at some point during this process.


other fun stuff
---------------

* you can use ``fab create_config`` to generate a configuration file for you, for any project.
* by default, ``create_config()`` writes the resulting config to `./conf/deploy.ini` (within the repo)
* ``fab create_config:outfile=~/my_app.ini`` will let you specify where the configuration file is actually written.
* you can supply your own configuration to ``deploy_project()``, eg: ``fab deploy_project:config=/path/to/custom.conf``
