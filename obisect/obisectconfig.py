#!/usr/bin/env python3
import os

shell = ['/bin/bash', '-i', '-c']  # bash with sourced ~/.bashrc for alias. use empty list to use default shell or define your own
default_repos = ['odoo', 'enterprise']  # make alias work. use empty list to use default shell or define your

# repo path format. repo or ../repo depending on position
# can be adapted to match worktrees containing version in path '{repo_name}/master' or use custom logic with os.getcwd()

repo_path = '{repo_name}'
if not os.path.isdir(repo_path.format(repo_name=default_repos[-1])):
    repo_path = '../{repo_name}'

if not os.path.isdir(repo_path.format(repo_name=default_repos[-1])):
    raise Exception(f"%s doesn't look to be a directory. check the config file at {__file__}" % repo_path.format(repo_name=default_repos[-1]))
