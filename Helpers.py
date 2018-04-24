import subprocess
import re

branch_heights = {}
BRANCH_DIST = 30
max_height = 20


class CommitPoint:
    def __init__(self, sha, date, branch):
        self.sha = sha
        self.date = date
        self.branches = [branch]
        self.x = None
        self.y = None
        self.tag = None

    def point(self):
        st = '<circle cx="%d" cy="%d" r="4" stroke="black" />\n' % (self.x, self.y)
        if self.tag:
            st += '<text x="%d" y="%d" transform="rotate(-45 %d %d)">%s</text>\n' % (self.x,
                                                                                     self.y - 5,
                                                                                     self.x,
                                                                                     self.y - 5,
                                                                                     self.tag)
        return st


class BranchLine:
    def __init__(self, name, commits):
        self.points = []
        self.name = name
        for c in commits:
            if name in c.branches:
                self.points.append((c.x, c.y))

    def line(self):
        text_height = get_branch_height(None, self.name) + 50
        st = ''
        for i, p in enumerate(self.points[:-1]):
            st += '<line x1="%d" y1="%d" x2="%d" y2="%d" style="stroke:rgb(255,0,0);' \
                  'stroke-width:2" />\n' % (self.points[i][0],
                                            self.points[i][1],
                                            self.points[i + 1][0],
                                            self.points[i + 1][1])
        st += '<text x="%d" y="%d" fill="red" transform="rotate(45 %d %d)">%s</text>\n' % (self.points[-1][0],
                                                                                           text_height,
                                                                                           self.points[-1][0],
                                                                                           text_height,
                                                                                           self.name)
        st += '<line x1="%d" y1="%d" x2="%d" y2="%d" '\
              'style="stroke:rgb(0,255,0);stroke-width:2;" />\n' % (self.points[-1][0],
                                                                    self.points[-1][1],
                                                                    self.points[-1][0],
                                                                    text_height)
        return st


def add_to_commits(coms, sha, date, branch):
    for c in coms:
        if c.sha == sha:
            c.branches.append(branch)
            return
    coms.append(CommitPoint(sha, date, branch))


def get_branch_height(commit, name=None):
    global branch_heights, max_height
    if name:
        if name not in branch_heights:
            max_height += BRANCH_DIST
            branch_heights[name] = max_height
            return max_height
        return branch_heights[name]
    h_lst = []
    for b in branch_heights:
        if b in commit.branches:
            h_lst.append(branch_heights[b])
    if h_lst:
        return min(h_lst)
    max_height += BRANCH_DIST
    branch_heights[commit.branches[0]] = max_height
    return max_height


def get_all_branches():
    branches = []
    branch_output = subprocess.check_output(['git', 'branch', '-a'])
    pat = re.compile('(remotes/origin/.*)')
    for line in branch_output.split('\n'):
        m = pat.search(line)
        if m:
            if 'HEAD' not in m.group(1):
                branches.append(m.group(1))
    return branches
