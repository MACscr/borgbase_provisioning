# borgbase_provisioning
Work in Progress Ansible playbook and script. Adapted from official borgbase client. Relies on https://github.com/borgbase/ansible-role-borgbackup

Example playbook settings. I use these for my APNSCP servers:

```
    borg_source_directories:
      - /home/virtual
    borg_exclude_patterns:
      - /home/virtual/FILESYSTEMTEMPLATE
      - /home/virtual/site*/fst
      - /home/virtual/site*/shadow/var/lib/mysql
      - /home/virtual/site*/shadow/var/lib/pgsql
    borg_retention_policy:
      keep_hourly: 3
      keep_daily: 7
      keep_weekly: 4
      keep_monthly: 6
 ```

The 'borg_passphrase' variable is set in /etc/hosts like so:

```
[apnscp]
cp3.example.com borg_passphrase='T#gg43522%#fj9k'
cp4.example.com borg_passphrase='GEgd4%7774$AeLv6'
```
