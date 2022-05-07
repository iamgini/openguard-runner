# openguard-runner

OpenGuard Runner for remediating issues

# Installation

```shell
## download runner files
$ git clone https://github.com/ginigangadharan/openguard-runner.git
$ cd openguard-runner/

## Copy service file
$ cp etc_systemd_system_openguard-runner.service /etc/systemd/system/openguard-runner.service

## Reload daemon
$ systemctl daemon-reload

## Start OpenGuard Runner
$ systemctl start openguard-runner

## Checks status
root@CP-OpenGuard-Runner:/vagrant# systemctl status openguard-runner
● openguard-runner.service - OpenGuard Runner
     Loaded: loaded (/etc/systemd/system/openguard-runner.service; enable>
     Active: active (running) since Sat 2022-05-07 13:06:28 +08; 33s ago
   Main PID: 25433 (python3)
      Tasks: 1 (limit: 467)
     Memory: 21.6M
     CGroup: /system.slice/openguard-runner.service
             └─25433 /usr/bin/python3 /opt/openguard-runner/openguard-run>

May 07 13:06:28 CP-OpenGuard-Runner systemd[1]: Started OpenGuard Runner.


```