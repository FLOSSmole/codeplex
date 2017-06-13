#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it
# and/or modify it under the terms of GPL v3
#
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# Contribution from:
# Caroline Frankel
#
# We're working on this at http://flossmole.org - Come help us build
# an open and accessible repository for data and analyses for open
# source projects.
#
# If you use this code or data for preparing an academic paper please
# provide a citation to
#
# Howison, J., Conklin, M., & Crowston, K. (2006). FLOSSmole:
# A collaborative repository for FLOSS research data and analyses.
# Int. Journal of Information Technology & Web Engineering, 1(3), 17–26.
#
# and
#
# FLOSSmole(2004-2017) FLOSSmole: a project to provide academic access to data
# and analyses of open source projects. Available at http://flossmole.org
#
################################################################
# usage:
# 9parseCodeplexUsers.py <datasource_id> <db password>

# purpose:
# grab all the username, personal statement, date joined, and last visit date
# of each user stored on Codeplex before it was shut down
################################################################
import pymysql
import sys
from bs4 import BeautifulSoup

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

datasourceID = sys.argv[1]
pw = sys.argv[2]

dbuser = 'megan'
db = 'codeplex'
dbhost = 'flossdata.syr.edu'


# collects and inserts information on user to table
def info(username):
    print(username)

    userUrl = 'http://www.codeplex.com/site/users/view/' + username
    print(userUrl)

    # get user's html page
    req2 = urllib2.Request(userUrl, headers=hdr)
    userhtml = urllib2.urlopen(req2).read()

    soup2 = BeautifulSoup(userhtml, "html.parser")
    dates = soup2.find("div", id="user_left_column")

    # get date user became a member
    memberSinceList = dates.find("p").contents[1].contents[0]
    memberSince = date_converter(memberSinceList)
    print("memberSince: ", memberSince)

    # get the last time the user visited
    lastVisitList = dates.find("p").contents[5].contents[0]
    lastVisit = date_converter(lastVisitList)
    print("lastVisit: ", lastVisit)

    # get the user personal statement
    personal = soup2.find("div", id="user_right_column")
    personalStatement = personal.find("p")
    statement = ''

    if len(personalStatement.contents[1].contents[0]) == 1:
        code = personalStatement.find('div', {'class': 'wikidoc'}).contents
        for c in code:
            statement += str(c) + ' '
    else:
        statement = 'No personal statement has been written.'
    print(statement)
    cursor.execute(insertHTMLQuery, (datasourceID,
                                     username,
                                     statement,
                                     memberSince,
                                     lastVisit,
                                     userhtml))
    dbconn.commit()
    print(username, "inserted!")


# converts months into their number
def convertMonth(moName):
    months = {'January': '01',
              'February': '02',
              'March': '03',
              'April': '04',
              'May': '05',
              'June': '06',
              'July': '07',
              'August': '08',
              'September': '09',
              'October': '10',
              'November': '11',
              'December': '12'}
    return months[moName]


# converts date to YYYY-MM-DD format
def date_converter(listName):
    date = listName.split(' ')
    month = date[0]
    day = date[1].split(',')[0]
    year = date[2]
    monthNum = convertMonth(month)
    return '{}-{}-{}'.format(year, monthNum, day)

# Open remote database connection
dbconn = pymysql.connect(host=dbhost,
                         user=dbuser,
                         passwd=pw,
                         db=db,
                         use_unicode=True,
                         charset='utf8mb4',
                         autocommit=True)
cursor = dbconn.cursor()

selectProjectsQuery = 'SELECT proj_name \
                       FROM cp_projects_indexes \
                       WHERE datasource_id = %s'

selectProjectsIndexes = 'SELECT people_html \
                         FROM cp_projects_indexes \
                         WHERE datasource_id = %s \
                         AND proj_name = %s'

insertHTMLQuery = 'INSERT IGNORE INTO cp_project_people (datasource_id,\
                                                         username,\
                                                         personal_statement,\
                                                         member_since,\
                                                         last_visit,\
                                                         user_html,\
                                                         last_updated) \
                   VALUES (%s, %s, %s, %s, %s, %s, now())'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

cursor.execute(selectProjectsQuery, (datasourceID,))
projectList = cursor.fetchall()

for project in projectList:
    projectName = project[0]
    print('Project:', projectName)

    # grab the people page
    cursor.execute(selectProjectsIndexes, (datasourceID, projectName))
    peopleHtml = cursor.fetchone()[0]
    try:
        soup = BeautifulSoup(peopleHtml, "html.parser")
        div = soup.find('div', id='ProjectMembers')

        # Get all of the Coordinators
        listOfCoordinators = div.find("div", id="CoordinatorsContainer")
        coordinatorLine = listOfCoordinators.find_all('div', {'class': 'UserDetails'})

        for coordinator in coordinatorLine:
            username = coordinator.find('a').contents[0]
            info(username)

        # Get all of the Developers
        listOfDevelopers = div.find("div", id="DevelopersContainer")
        developerLine = listOfDevelopers.find_all('div', {'class': 'UserDetails'})

        for developer in developerLine:
            username = developer.find('a').contents[0]
            info(username)

        # Get all of the Editors
        listOfEditors = div.find("div", id="EditorsContainer")
        editorLine = listOfEditors.find_all('div', {'class': 'UserDetails'})

        for editor in editorLine:
            username = editor.find('a').contents[0]
            info(username)

    except pymysql.Error as error:
        print(error)
        dbconn.rollback()
    except:
        print()

dbconn.close()
