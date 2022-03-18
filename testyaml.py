import yaml
import sys

try:
  with open("/etc/openguard-runner/openguard-runner.yaml", 'r') as config:
    try: 
      read_data = yaml.load(config, Loader=yaml.FullLoader)
      print(read_data['access']['openguard_job_api_url'])
    except Exception as yamlexec:
      print("Error" + str(yamlexec))
      sys.exit(5)
except FileNotFoundError as filenotfound:
  print("Unable to read file" + str(filenotfound))
  sys.exit(5)
except Exception as exc:
  print("Unable to read file" + str(exc))
  sys.exit(5)
