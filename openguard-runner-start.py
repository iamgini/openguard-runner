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

try:
  with open("/etc/openguard-runner/openguard-runner.yaml", 'r') as config:
    try: 
      read_config = yaml.load(config, Loader=yaml.FullLoader)
      #print(read_config['access'])
    except Exception as yamlexec:
      print("Error" + str(yamlexec))
      sys.exit(5)
except FileNotFoundError as filenotfound:
  print("Unable to read file" + str(filenotfound))
  sys.exit(5)
except Exception as exc:
  print("Unable to read file" + str(exc))
  sys.exit(5)

openguard_job_api_url = read_config['access']['openguard_job_api_url']
auth_token = read_config['access']['token']
user_agent = read_config['environment']['agent_name']
check_interval = read_config['environment']['check_interval_in_seconds']
base_dir = read_config['environment']['base_directory']

## Fetch the job from openguard
## NEW !!!
def fetch_job():
  
  headers = {
      "Authorization": f"Token {auth_token}",
      'Content-Type' : 'application/json',
      }
  #base64string = base64.b64encode('%s' % (auth_token))
  #request.add_header("Authorization", "Basic %s" % base64string)  
  #request.add_header("Authorization", "Token %s" % base64string)
  
  request = urllib.request.Request(openguard_job_api_url, headers=headers)
  #result = urllib.request.urlopen(request)


  ## check details for urlopen results here:
  ## https://docs.python.org/3/library/urllib.request.html 
  try:
    with urlopen(request, timeout=10) as response:
      #app_logger("Fetching jobs")
      output = json.loads(response.read().decode('utf-8'))
      #print(response_data['pending_incidents'] + "OKAY")
      #output = response_data
      app_logger("Fetching jobs")
      pending_incidents =  output['pending_incidents']
      #print(pending_incidents)
      if pending_incidents == "YES":
        
        this_hostname = output['managed_node']
        node_connection_name = output['node_connection_name']
        rule_fix_playbook = output['rule_fix_playbook']
        this_incident_id = output['incident_id']
        node_connection_method = output['node_connection_method']
        node_connection_username = output['node_connection_username']
        node_connection_password = output['node_connection_password']
        node_connection_key = output['node_connection_key']
        node_connection_type = output['node_connection_type']
        #print(node_connection_key)
        app_logger("Found job(Incident: " + str(this_incident_id) + ") for " + str(this_hostname))
        if rule_fix_playbook != "NA":
          ## Call Ansible Runner
          app_logger("Running job(Incident: " + str(this_incident_id) + ") for " + str(this_hostname))
          ansible_output = run_ansible(this_hostname, node_connection_name, node_connection_username, node_connection_password, node_connection_key, node_connection_type, rule_fix_playbook)
          #app_logger("Ansible output " + str(ansible_output))
          #print(ansible_output)
          if ansible_output == 0:
            app_logger(str(this_hostname)  + " - executed " + str(rule_fix_playbook))
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

              post_job_update = requests.post(openguard_job_api_url, json=job_completed_data, 
                                            headers=headers)
              print(f"Status Code: {post_job_update.status_code}, Response: {post_job_update. json ()}")
              app_logger("Job(Incident: " + str(this_incident_id) + ") completed")

            except Exception as incident_entry_update_exception:
              print(incident_entry_update_exception)

      else:
        app_logger("No incidents found")
  except HTTPError as error:
      print(error.status, error.reason)
      app_logger(str(error.status) + "-" + str(error.reason))
  except URLError as error:
      print(error.reason)
      app_logger(str(error.reason))
  except TimeoutError:
      print("Request timed out")
      app_logger("Request timed out")
  except Exception as fetch_data_exeception:
    print("Unable to fetch job details.")
    print(fetch_data_exeception)
    app_logger("Unable to fetch job details." + str(fetch_data_exeception))
    

## Ansible runner 
def run_ansible(node_names, ansible_host_name, node_connection_username, node_connection_password, node_connection_key, node_connection_type, playbook_file):

    ## varialble
    app_logger(str(node_names)  + " - executing " + str(playbook_file))
    inventory_file = base_dir + '/ansible_data/inventory/this_inventory'
    #print(node_connection_type)
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
    if node_connection_type == 'Username-Password':
        hosts = {
            'hosts': {
                node_names: {
                    'ansible_host': ansible_host_name,
                    'ansible_user': node_connection_username,
                    'ansible_password': node_connection_password,
                    'ansible_ssh_common_args': ' -o StrictHostKeyChecking=no ',
                }
            },
        }
    else:
        ssh_file = open( base_dir + "/ansible_data/env/ssh_key", "w")
        ssh_file.write(node_connection_key)
        ssh_file.close() 
        hosts = {
            'hosts': {
                node_names: {
                    'ansible_host': ansible_host_name,
                    'ansible_user': node_connection_username,
                    'ansible_ssh_common_args': '-o StrictHostKeyChecking=no'
                }
            },
        }
    print(hosts)

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
        'inventory': {'all': hosts},
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

fetch_job()

#while True:
#  time.sleep(check_interval)
#  fetch_job()

try:
    app_logger("Starting OpenGuard Runner...")
    while False:
        fetch_job()
        time.sleep(check_interval)
        try:
            f = open(base_dir + "/og.stop")
            app_logger("Stopping OpenGuard Runner...")
            # stop the application
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
   
