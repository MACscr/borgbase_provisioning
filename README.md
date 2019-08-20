# borgbase_provisioning
Work in Progress Ansible playbook and script. Adapted from official borgbase client. Relies on https://github.com/borgbase/ansible-role-borgbackup

Don't forget to set the following in the playbook:

```
    borg_source_directories:
      - /home/virtual
    borg_exclude_patterns:
      - /srv/www/old-sites
    borg_retention_policy:
      keep_hourly: 3
      keep_daily: 7
      keep_weekly: 4
      keep_monthly: 6
 ```
