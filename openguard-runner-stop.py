import yaml
import sys
import time
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

base_dir = read_config['environment']['base_directory']
## fetch the interval and wait for 3x times
check_interval = read_config['environment']['check_interval_in_seconds'] * 2
#print(check_interval)

try:
  stop_file = open( base_dir + "/og.stop", "w")
  stop_file.write( "Stop" )
  stop_file.close()  
  print("Stop file created")
except Exception as exc:
  print("Unable to create stop file" + str(exc))
  sys.exit(5)
finally:
  try:
    stop_file.close()
  except:
    pass  

## wait for 3x time of actual check_interval
time.sleep(check_interval)

try:
  os.remove( base_dir + "/og.stop" )
  print("Stop file deleted")
except Exception as exc:
  print("Unable to delete stop file" + str(exc))
  sys.exit(5)

