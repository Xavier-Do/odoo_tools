#!/usr/bin/env python3

import logging
import re
import sys
import urllib.request

_logger = logging.getLogger(__name__)


class bcolors:
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

if len(sys.argv) < 2:
    print("please provide build number")
    exit()

buildNumber = sys.argv[1]
update_mode = ''
if len(sys.argv) > 2:
    update_mode = sys.argv[2]


"""
acces to full all log from build number
"""
gen_url = "http://runbot.odoo.com/runbot/build/" + buildNumber
text = urllib.request.urlopen(gen_url).read().decode('utf-8')
p = re.compile(r'http:\/\/runbot(\d+).odoo.com\/runbot\/static\/build\/(.*)\/logs\/(test_only).txt')
data = p.search(text, re.MULTILINE)
runbot = data.group(1)
build = data.group(2)
log = data.group(3)
logs_url = f'http://runbot{runbot}.odoo.com/runbot/static/build/{build}/logs/{log}.txt'
full_log_text = urllib.request.urlopen(logs_url).read().decode('utf-8')
_logger.info("Scanning %s", logs_url)

p = re.compile(r'Query count (more|less) than expected for user (__system__|emp): (\d+) (>|<) (\d+) in (.*) at (.+\.py):(\d+)')
query_data = p.findall(full_log_text, re.MULTILINE)
print("%s query count changes " % len(query_data))
lines = []
update = False
for elem in query_data:
    (diff_type, user, actual, sign, expected, function_name, filepath, line_number) = elem
    expected = int(expected)
    line_number = int(line_number)
    actual = int(actual)
    if "test_mail" in filepath:
        filepath = "./odoo/addons/test_mail%s" % filepath.split("test_mail")[1]
        with open(filepath, 'r+') as f:
            lines = f.readlines()
            line = lines[line_number]
            diff = 0
            # linenumber is not the line "with self.assertQueryCount(", we need to find the closest on top direction
            while line_number > 0 and "self.assertQueryCount(" not in line:
                line_number -= 1
                line = lines[line_number]
                diff += 1
            if line_number < 0:
                print("ERROR: impossible to match corresponding assert")
                continue
            elif diff > 6:
                print("WARNING, assert found at %s line from source" % diff)
            tag = bcolors.FAIL
            more = False
            less = False
            if actual > expected:
                tag = bcolors.WARNING
                more = True
            elif actual < expected:
                tag = bcolors.OKGREEN
                less = True
            newline = line
            if "%s=%s" % (user, expected) in line:
                newline = line.replace("%s=%s" % (user, expected), "%s=%s" % (user, actual))
            else:
                print("Unexpected line %s. Please check and improve if needed" % line)
                print(elem)
                break
            if line != newline:
                print("%s Replacing by '%s'%s" % (tag, newline.strip(), bcolors.ENDC))
                lines[line_number] = newline  # do something better
                if ('*' in update_mode) or (more and ('+' in update_mode)) or (less and ('-' in update_mode)):
                    f.seek(0)
                    f.writelines(lines)
                    f.truncate()
                    print('updated')
            else:
                print("%s No replacement '%s'%s" % (bcolors.OKBLUE, line.strip(), bcolors.ENDC))
    else:
        print("ignored: not a test_mail %s" % filepath)
