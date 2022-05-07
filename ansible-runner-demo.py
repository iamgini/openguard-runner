## Execute the fix job in OpenGuard by calling the API

import time
import urllib.request
import urllib.parse
from urllib.request import urlopen
import json
import requests
from datetime import datetime
import ansible_runner
import base64
from urllib.error import HTTPError, URLError

import yaml
import sys
import os

## logging config start
# import logging
# logging.basicConfig(level=logging.DEBUG)
## logging config end

## Ansible runner 
def run_ansible():

    inventory_file = 'ansible_data/inventory/this_inventory'
    hosts = {
        'hosts': {
            'ubuntu': {
                'ansible_host': '192.168.56.35',
                'ansible_user': 'devops',
                'ansible_password': 'devops',
                'ansible_ssh_common_args': ' -o StrictHostKeyChecking=no ',
            }
        },
    }
    
    print(hosts)


    ## create file manually due to persmission issue
    this_inventory = "Ubuntu-20-CP ansible_host=192.168.56.35 ansible_user=devops ansible_password=devops"
    new_inventory = open(inventory_file, "w")
    new_inventory.write(this_inventory)
    new_inventory.close()


    ## fetch and assign extra variables
    extravars = {
        'NODES': 'all'
    }

    ## build kwargs for passing to runner
    kwargs = {
        'playbook': 'test.yaml',
        'inventory': {'all': hosts},
        #'inventory': inventory_file,
        #'envvars': envvars,
        'extravars': extravars,
        'private_data_dir': 'ansible_data'
    }


    print("exec mode")
    #ansiblerunner = ansible_runner.run(private_data_dir='ansible_data', 
    #                       playbook='test.yml')

    ## run ansible_runner with **kwargs

    ansiblerunner = ansible_runner.run(**kwargs)
    print("hhh")

    #print("{}: {}".format(ansiblerunner.status, ansiblerunner.rc))
    # successful: 0
    #for each_host_event in ansiblerunner.events:
    #   print(each_host_event['event'])
    #print("Final status:")
    #print(ansiblerunner.stats)

    ## delete the hosts.json file
    try:
        os.remove( base_dir + "/ansible_data/inventory/hosts.json" )
        #print("Stop file deleted")
    except Exception as exc:
        #print("Unable to delete host file" + str(exc))
        sys.exit(5)

    #remove ssh key
    try:
        ssh_file = open( base_dir + "/ansible_data/env/ssh_key", "w")
        ssh_file.write('')
        ssh_file.close()
    except Exception as exc:
        #print("Unable to delete key file" + str(exc))
        sys.exit(5)
    
    #try:
    #    os.remove( base_dir + "/ansible_data/env/ssh_key" )
    #    #print("Stop file deleted")
    #except Exception as exc:
    #    #print("Unable to delete key file" + str(exc))
    #    sys.exit(5)



    return ansiblerunner.rc

def app_logger(log_message):
    dateTimeObj = datetime.now()
    timestampStr = str(dateTimeObj.strftime("%Y-%b-%d-%H:%M:%S"))
    new_log = open( base_dir + '/application_logs/logs', "a")
    log_line = timestampStr + ": " + log_message
    new_log.write(log_line + '\n' )
    print(log_line)
    new_log.close()    

## debug mode testng, comment below line
run_ansible()
