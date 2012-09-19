'''
Install PDS
-----------

details at oms-deploy! https://github.com/IDCubed/oms-deploy
'''

from oms_fabric.webapp import Webapp

PDS = Webapp()
PDS.repo_url = 'https://github.com/IDCubed/OMS-PDS'
PDS.repo_name = 'OMS-PDS'

def deploy_project(instance='pds',
                   branch='master',
                   config='./conf/deploy.ini'):
    '''
    direct pull from fabfile.py in resource server, not tested and needs more
    work, just exemplifying the idea.
    '''
    PDS.branch = branch
    PDS.deploy_project(instance, config, branch)


def create_config(outfile='./conf/deploy.ini'):
    ''' 
    ask the user some questions, create a configuration, and write to outfile
    '''
    user_config(outfile)
