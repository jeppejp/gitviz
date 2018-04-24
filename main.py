#!/usr/bin/python
import subprocess
import re
import tempfile
from Helpers import *


branch_lines = []
commits = []
branches = []

branch_output = subprocess.check_output(['git', 'branch', '-a'])
pat = re.compile('(remotes/origin/.*)')
for line in branch_output.split('\n'):
    m = pat.search(line)
    if m:
        if 'HEAD' not in m.group(1):
            branches.append(m.group(1))

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


commits.sort(key=lambda x: x.date)

print "Plotting %d commits and %d branches" % (len(commits), len(branches))

i = 5
for c in commits:
    c.x = i
    c.y = get_branch_height(c)
    i += 10


for b in branches:
    branch_lines.append(BranchLine(b, commits))

fn = tempfile.mktemp()
with open(fn, 'w') as fp:
    fp.write('<!DOCTYPE html>')
    fp.write('<html><body>')

    fp.write('<svg height="%d" width="%d">' % (400 + len(branches) * 50, 400 + (len(commits) * 10)))

    for c in commits:
        fp.write(c.point())

    for b in branch_lines:
        fp.write(b.line())

    fp.write('</svg></body></html>')

print "Wrote output to %s opening in browser" % (fn)
subprocess.check_output(['x-www-browser', fn])
