# -*- coding: utf-8 -*-

"""
    Script for generation mindmap for XMind tool from YouTrack
"""

__author__ = "Oleksandr Pylkevych"
__email__ = "o.pylkevych@gmail.com"
__version__ = 0.4

import os
import sys

import config
import xmind
from xmind.core.topic import TopicElement

parentdir = os.path.dirname(os.path.abspath(__file__))
libdir = parentdir + '/youtrack/'
sys.path.append(libdir)
from youtrack.connection import Connection

passwd = open('password.txt', 'r').read().strip()
user = config.USERNAME
server = 'https://106.125.46.213/youtrack/'
connection = Connection(server, user, passwd)

category = config.CATEGORY

print category + ' mindmap creation...'

# Get array of issues
issues_list = connection.getIssues('TRAR', 'Category: ' + category + ' State: -Obsolete sort by: {issue id} asc', 0, 2000)

issue_map = xmind.load(category + ".xmind")
sheet = issue_map.getPrimarySheet()
sheet.setTitle(category)
root_primary = sheet.getRootTopic()
root_primary.setTitle(category)


def getSuperParents(issues):
    parent_dict = dict()
    for issue in issues:
        parent_dict[issue.id] = (connection.getIssues('TRAR', 'Category: ' + category + ' State: -Obsolete Parent for: ' + issue.id, 0, 2000))
    parents = []
    for s in range(len(parent_dict.items())):
        if not parent_dict.items()[s][1]:
            parents.append(parent_dict.items()[s][0])
    return parents


def getSubtasks(Id):
    return connection.getIssues('TRAR', 'Subtask of: ' + Id + ' State: -Obsolete', 0, 2000)


def setImpStatus(issue_id):
    issue_status = connection.getIssue(issue_id)['UI Implementation status']
    if issue_status == 'Not implemented':
        return 'star-red'
    elif issue_status == 'Blocked':
        return 'star-orange'
    elif issue_status == 'Partially implemented':
        return 'star-purple'
    elif issue_status == 'Implemented':
        return 'star-green'
    else:
        pass


def setPriority(issue_id):
    issue_priority = connection.getIssue(issue_id)['Priority']
    if issue_priority == 'Minor':
        return 'priority-5'
    elif issue_priority == 'Normal':
        return 'priority-4'
    elif issue_priority == 'Major':
        return 'priority-3'
    elif issue_priority == 'Critical':
        return 'priority-2'
    elif issue_priority == 'Show-stopper':
        return 'priority-1'


def setState(issue_id):
    issue_state = connection.getIssue(issue_id)['State']
    if issue_state == 'Draft':
        return 'symbol-exclam'
    elif issue_state == 'PL review':
        return 'people-orange'
    elif issue_state == 'Dev review':
        return 'people-blue'
    elif issue_state == 'Clarification':
        return 'symbol-question'
    elif issue_state == 'Fixed':
        return 'people-green'


# TODO: Implement method
def setIssueNotes(issue_id):
    issue = connection.getIssue(issue_id)


def getCommentsByID(issue_id):
    comments = ''
    for i in connection.getIssue(issue_id).getComments():
        comments += "[" + i.authorFullName + "]" + "\n" + i.text + '\n\n' 
    return comments.encode('utf-8')


def getChild(issue_id, level, t):
    # print level, Id
    top = TopicElement()
    # Split on '->' due to issue title on TRAR project
    top.setTitle(connection.getIssue(issue_id).summary.split('->')[-1])
    top.addMarker(setImpStatus(issue_id))
    top.addMarker(setPriority(issue_id))
    top.addMarker(setState(issue_id))
    top.setURLHyperlink(server + 'issue/' + issue_id)
    comments = getCommentsByID(issue_id)
    if len(comments) > 0:
        top.setPlainNotes(comments)
    t.addSubTopic(top)
    for i in getSubtasks(issue_id):
        getChild(i.id, level+1, top)

for parent in getSuperParents(issues_list):
    getChild(parent, 0, root_primary)

xmind.save(issue_map, category + ".xmind")

print category + '.xmind' + ' created'
