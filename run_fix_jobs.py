## Execute the fix job in OpenGuard by calling the API

import time
import urllib.request
from urllib.request import urlopen
import json
import requests
from datetime import datetime
import ansible_runner


openguard_job_api_url = 'http://192.168.56.1:8000/api/incident_fix/'
check_for_jobs = True
## interval in seconds
check_interval = 5
base_dir = '/vagrant'

## Fetch the job from openguard
def fetch_job():
  try:
    #source = requests.get(openguard_job_api_url).json()
    data = urllib.request.urlopen(openguard_job_api_url).read()
    output = json.loads(data)
    #print(output)
    app_logger("Fetching jobs")
    pending_incidents =  output['pending_incidents']
    print(pending_incidents)
    if pending_incidents == "YES":
      
      this_hostname = output['managed_node']
      node_connection_name = output['node_connection_name']
      rule_fix_playbook = output['rule_fix_playbook']
      this_incident_id = output['incident_id']
      app_logger("Found jobs for " + str(this_hostname))
      if rule_fix_playbook != "NA":
        ## Call Ansible Runner
        app_logger("Running jobs for " + str(this_hostname))
        ansible_output = run_ansible(this_hostname, node_connection_name,rule_fix_playbook)
        #app_logger("Ansible output " + str(ansible_output))
        #print(ansible_output)
        if ansible_output == 0:
          try:
            #pass
            incident_status = 'FIXED'
            incident_time_fixed = datetime.now()
            incident_fix_comments = 'Updated item ' + str(this_incident_id)
            #incident_id = this_incident_id
            job_completed_data = { "incident_id": str(this_incident_id),
                                        "incident_time_fixed": str(incident_time_fixed),
                                        "incident_status": incident_status,
                                        "incident_fix_comments": incident_fix_comments,
                                      }
            #print(job_completed_data)                                  
            #job_completed_data_new =  json.load(job_completed_data)
            #headers = {'Authorization' : ‘(some auth code)’, 'Accept' : 'application/json',    'Content-Type' : 'application/json'}
            headers = {'Content-Type' : 'application/json'}

            post_job_update = requests.post(openguard_job_api_url, json=job_completed_data,     headers=headers)
            #print(job_completed_data)
            #print(post_job_update.json())
            print(f"Status Code: {post_job_update.status_code}, Response: {post_job_update. json ()}")
            app_logger(str(this_hostname)  + " - executed " + str(rule_fix_playbook))

            #incident.save()
          except Exception as incident_entry_update_exception:
            print(incident_entry_update_exception)

          
          #dateTimeObj = datetime.now()
          #timestampStr = str(dateTimeObj.strftime("%Y-%b-%d-%H:%M:%S"))
#
          #new_log = open( base_dir + '/application_logs/logs', "a")
          #new_log.write( timestampStr + ": " + str(this_hostname)  + " - executed " + str   #(rule_fix_playbook) + '\n')
          ##new_log.write('\n'  + json.dumps( incident.    #incident_time_reported ))
          #new_log.close()
    else:
      app_logger("No incidents found")
      #dateTimeObj = datetime.now()
      #timestampStr = str(dateTimeObj.strftime("%Y-%b-%d-%H:%M:%S"))
      #new_log = open( base_dir + '/application_logs/logs', "a")
      #new_log.write( timestampStr + ": No incidents found" + '\n')
      #print(timestampStr + ": No incidents found")
      #new_log.close()

  except Exception as fetch_data_exeception:
    print("Unable to fetch data.")
    print(fetch_data_exeception)
    #time.sleep(check_interval)

## Ansible runner 
def run_ansible(node_names, ansible_host_name, playbook_file):

    ## varialble
    app_logger(str(node_names)  + " - executing " + str(playbook_file))
    inventory_file = base_dir + '/ansible_data/inventory/this_inventory'
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
        'private_data_dir': base_dir + '/ansible_data'
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

def app_logger(log_message):
    dateTimeObj = datetime.now()
    timestampStr = str(dateTimeObj.strftime("%Y-%b-%d-%H:%M:%S"))
    new_log = open( base_dir + '/application_logs/logs', "a")
    log_line = timestampStr + ": " + log_message
    new_log.write(log_line + '\n' )
    print(log_line)
    new_log.close()    
#fetch_job()

#while True:
#  time.sleep(check_interval)
#  fetch_job()

try:
    while True:
        fetch_job()
        time.sleep(check_interval)
        try:
            f = open(base_dir + "/og.lock")
            # Do something with the file
            break
        except FileNotFoundError:
            pass
        finally:
            try:
                f.close()
            except:
                pass
except KeyboardInterrupt:
    print("Press Ctrl-C to terminate the script")
    pass
