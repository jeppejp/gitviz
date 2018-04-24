#!/usr/bin/python
import subprocess
import re
import tempfile
from Helpers import *
import argparse
import sys


parser = argparse.ArgumentParser(description='GitViz')
parser.add_argument('-o', '--output', action='store',
                    help='Specify the output file. Creates random tmp file per default')
parser.add_argument('-f', '--fetch', action='store_true',
                    help='Run \'git fetch --all\' before starting')
parser.add_argument('-b', '--browser', action='store_true',
                    help='Open the output using x-www-browser')

args = parser.parse_args(sys.argv[1:])


# Run git fetch --all if specified. Required to get all info from all branches
if args.fetch:
    subprocess.check_output(['git', 'fetch', '--all'])

branch_lines = []
commits = []
branches = get_all_branches()


# try to sort the branches
for kw in ['master', 'release-', 'develop']:
    for b in branches:
        if kw in b:
            get_branch_height(None, name=b)


for branch in branches:
    output = subprocess.check_output(['git', 'log', '--format="%H %at"', branch])
    for line in output.split('\n'):
        spl = line.replace('"', '').split(' ')
        if len(spl) == 2:
            sha = spl[0]
            date = spl[1]
            add_to_commits(commits, sha, date, branch)


tags = subprocess.check_output(['git', 'tag'])
for tag in tags.split('\n'):
    if len(tag) > 0:
        tag_log = subprocess.check_output(['git', 'log', '--format="%H"', tag])
        sha = tag_log.split('\n')[0].replace('"', '')
        for c in commits:
            if c.sha == sha:
                c.tag = tag
                continue


# Sort commits by date - oldest first
commits.sort(key=lambda x: x.date)


i = 5
for c in commits:
    c.x = i
    c.y = get_branch_height(c)
    i += 10


for b in branches:
    branch_lines.append(BranchLine(b, commits))

if args.output:
    fn = args.output
else:
    fn = tempfile.mktemp() + '.html'

with open(fn, 'w') as fp:
    fp.write('<!DOCTYPE html>\n')
    fp.write('<html><body>\n')

    fp.write('<svg height="%d" width="%d">\n' % (400 + len(branches) * 50, 400 + (len(commits) * 10)))

    for c in commits:
        fp.write(c.point())

    for b in branch_lines:
        fp.write(b.line())

    fp.write('</svg>\n</body>\n</html>')

if not args.output:
    # If output not specified print the name of the tempfile generated
    print "Output generated in %s" % (fn)
if args.browser:
    subprocess.check_output(['x-www-browser', fn])
