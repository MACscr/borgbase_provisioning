#!/ansible_launchpad/bin/python

import requests
import subprocess
import argparse
import sys
import os.path

# Define the parser
parser = argparse.ArgumentParser(description='Borgbase Repo Creator')
parser.add_argument('-token', action="store", dest='token', default=0)
parser.add_argument('-hostname', action="store", dest='hostname', default=0)
args = parser.parse_args()

if len(sys.argv) < 4:
    sys.stderr.write("Required Arguments: -token xx.yy.zz -hostname localhost")
    sys.exit(1)


REPO_DETAILS = '''
query repoList {
  repoList {
    id
    name
    quota
    quotaEnabled
    lastModified
    currentUsage
  }
}
'''

SSH_ADD = '''
mutation sshAdd(
  $name: String!
  $keyData: String!
  ) {
    sshAdd(
      name: $name
      keyData: $keyData
    ) {
      keyAdded {
        id
        name
        hashMd5
        keyType
        bits
      }
    }
}
'''

REPO_ADD = '''
mutation repoAdd(
  $name: String
  $quota: Int
  $quotaEnabled: Boolean
  $appendOnlyKeys: [String]
  $fullAccessKeys: [String]
  $alertDays: Int
  $region: String
  $borgVersion: String
  ) {
    repoAdd(
      name: $name
      quota: $quota
      quotaEnabled: $quotaEnabled
      appendOnlyKeys: $appendOnlyKeys
      fullAccessKeys: $fullAccessKeys
      alertDays: $alertDays
      region: $region
      borgVersion: $borgVersion
    ) {
      repoAdded {
        id
        name
        region
        repoPath
      }
    }
}
'''

class GraphQLClient:
    def __init__(self, token, endpoint='https://api.borgbase.com/graphql'):
        self.endpoint = endpoint
        self.token = token

    def execute(self, query, variables=None):
        return self._send(query, variables)

    def _send(self, query, variables):
        data = {'query': query,
                'variables': variables}
        headers = {'Accept': 'application/json',
                   'Content-Type': 'application/json',
                   "Authorization": "Bearer " + self.token,
                   }

        request = self.session.post(self.endpoint, json=data, headers=headers)

        if request.status_code != 200:
            raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, query))

        return request.json()

# get short hostname
hostname = args.hostname

client = GraphQLClient(args.token)

# check if repo already exists at borgbase with name of hostname
res = client.execute(REPO_DETAILS)
for repo in res['data']['repoList']:
    if repo['name'] == hostname:
        sys.stderr.write("Repo already exists\n")
        sys.exit(0)

# lets create an ssh key if it does not exist
if (not os.path.exists('/root/.ssh/id_ed25519')):
    subprocess.call('ssh-keygen -t ed25519 -N "" -f /root/.ssh/id_ed25519 >/dev/null', shell=True)

f = open("/root/.ssh/id_ed25519.pub")
borg_pub = f.read()

new_key_vars = {
    'name': hostname,
    'keyData': borg_pub
}

# add host ssh key to borgbase
res = client.execute(SSH_ADD, new_key_vars)
new_key_id = res['data']['sshAdd']['keyAdded']['id']

new_repo_vars = {
    'name': hostname,
    'quotaEnabled': False,
    'fullAccessKeys': [new_key_id],
    'region': 'us',
    'alertDays': 2
}
# create repo
res = client.execute(REPO_ADD, new_repo_vars)
new_repo = res['data']['repoAdd']['repoAdded']['repoPath']

# ensure facts directory exists and create if it does not
subprocess.call('mkdir -p /etc/ansible/facts.d', shell=True)

# lets create a fact with the repo info
f = open("/etc/ansible/facts.d/borgbase_repo.fact", "w")
f.write('"{}"'.format(new_repo))
f.close()

print '{}'.format(new_repo)
