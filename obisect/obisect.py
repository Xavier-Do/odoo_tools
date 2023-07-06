#!/usr/bin/env python3
import argparse
import requests
import subprocess
import sys
import obisectconfig as config

from ast import literal_eval

parser = argparse.ArgumentParser()
parser.add_argument('good')
parser.add_argument('bad')
parser.add_argument('-r', nargs='+', help='Repos', dest='repos')
parser.add_argument('-c', nargs='+', help='Command', dest='command')
args = parser.parse_args()

good = args.good
bad = args.bad
repos = args.repos or config.default_repos
command = args.command

# fetch batch list
url = f"https://runbot.odoo.com/list_json?c_start={good}&c_stop={bad}"
response = requests.get(url)
if response.status_code != 200:
    url = f"https://runbot.odoo.com/list_json?start={good}&stop={bad}"
    response = requests.get(url)
    if response.status_code != 200:
        print("%s returned a status code %s" % (url, response.status_code))
        sys.exit(1)
content = response.text.strip()
batches = literal_eval(content)

# uniquify batches depending on used repos
unique_batches = {}
for batch in batches:
    unique_batches[tuple([batch['commits'][repo] for repo in repos])] = batch

batches = list(unique_batches.values())

def test(batch):
    print("Testing batch %s" % batch['batch_id'])
    for repo_name in repos:
        sha = batch['commits'][repo_name]
        repo_path = config.repo_path.format(repo_name=repo_name)
        subprocess.run(['git', '-C', repo_path, 'checkout', '-q', sha], check=True)
        print('- Checkouting %s in %s' % (sha, repo_path))
    if command:
        return subprocess.run(config.shell + [' '.join(command)], check=False).returncode == 0
    else:
        response = ''
        while response.lower() not in ('good', 'bad'):
            response = input("Enter 'good' or 'bad':\n")
        return response == 'good'

def bisect(batches):
    lo = 0
    hi = len(batches)
    while lo < hi:
        mid = (lo+hi)//2
        batch = batches[mid]
        success = test(batch)
        if not success:
            hi = mid
        else:
            lo = mid+1
    return lo

index = bisect(batches)

if index >= len(batches):
    print('No failing batch found')
elif index == 0:
    print('All batch failed')
else:
    batch = batches[index]
    print('First failing batch: %s' % batch['batch_id'])
    print('\n'.join('%s: %s' % commit for commit in batch['commits'].items() if commit[0] in repos))
