## Execute the fix job in OpenGuard by calling the API

import time
import urllib.request
from urllib.request import urlopen
import json

from datetime import datetime
import ansible_runner

openguard_job_api_url = 'http://192.168.56.1:8000/api/incident_fix/'
check_for_jobs = True
## interval in seconds
check_interval = 5

## Fetch the job from openguard
def fetch_job():
  try:
    #source = requests.get(openguard_job_api_url).json()
    data = urllib.request.urlopen(openguard_job_api_url).read()
    output = json.loads(data)
    print(output)
    this_hostname = output['managed_node']
    node_connection_name = output['node_connection_name']
    rule_fix_playbook = output['rule_fix_playbook']

    ## Call Ansible Runner
    ansible_output = run_ansible(this_hostname, node_connection_name,rule_fix_playbook)
    print(ansible_output)
    if ansible_output == 0:
      try:
        pass
        #incident.incident_status = 'FIXED'
        #incident.incident_time_fixed = timezone.now
        #incident.incident_fix_comments = 'Updated item ' + str(incident.id)
        #incident.save()
      except Exception as incident_entry_update_exception:
        print(incident_entry_update_exception)

      dateTimeObj = datetime.now()
      timestampStr = str(dateTimeObj.strftime("%Y-%b-%d-%H:%M:%S"))

      new_log = open( 'application_logs/logs', "a")
      new_log.write('\n' + timestampStr + ": " + str(this_hostname)  + " - executed " + str(rule_fix_playbook))
      #new_log.write('\n'  + json.dumps( incident.    #incident_time_reported ))
      new_log.close()

  except Exception as fetch_data_exeception:
    print("Unable to fetch data.")
    print(fetch_data_exeception)
    #time.sleep(check_interval)

## Ansible runner 
def run_ansible(node_names, ansible_host_name, playbook_file):

    ## varialble
    inventory_file = 'ansible_data/inventory/this_inventory'
    ## create inventory
    #hosts = {
    #    'hosts': {
    #        'Ubuntu-20-CP': {
    #            'ansible_host': '192.168.56.35',
    #            'ansible_user': 'devops',
    #            'ansible_password': 'devopssssss'
    #        }
    #    },
    #}
    #print(hosts)
    
    ## create file manually due to persmission issue
    this_inventory = node_names + " ansible_host=" + ansible_host_name + " ansible_user=devops ansible_password=devops "
    new_inventory = open(inventory_file, "w")
    new_inventory.write(this_inventory)
    new_inventory.close()

    ## fetch and assign extra variables
    extravars = {
        'NODES': node_names
    }

    ## build kwargs for passing to runner
    kwargs = {
        'playbook': playbook_file,
        #'inventory': {'all': hosts},
        #'inventory': inventory_file,
        #'envvars': envvars,
        'extravars': extravars,
        'private_data_dir': 'ansible_data'
    }

    #ansiblerunner = ansible_runner.run(private_data_dir='ansible_data', 
    #                       playbook='test.yml')

    ## run ansible_runner with **kwargs
    ansiblerunner = ansible_runner.run(**kwargs)

    #print("{}: {}".format(ansiblerunner.status, ansiblerunner.rc))
    # successful: 0
    #for each_host_event in ansiblerunner.events:
    #   print(each_host_event['event'])
    #print("Final status:")
    #print(ansiblerunner.stats)
    return ansiblerunner.rc
      
fetch_job()

#while check_for_jobs:
#  try:
#    
#    #with urllib.request.urlopen(openguard_job_api_url) as get_data:
#      get_data = urlopen(openguard_job_api_url)
#      print(get_data.read().decode('utf-8'))
#      print(type(get_data.read().decode('utf-8')))
#      
#      get_response = json.loads(get_data.read())
#      print(type(type(get_response)))
#    #print('hello')
#
#      time.sleep(check_interval)
#  except Exception as fetch_data_exeception:
#    print("Unable to fetch data.")
#    print(fetch_data_exeception)
#    time.sleep(check_interval)
  