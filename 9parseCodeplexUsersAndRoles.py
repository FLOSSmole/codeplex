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
# 9parseCodeplexUsersAndRoles.py <datasource_id> <db password>

# purpose:
# grab all the projects, contributors, their role, and how long they have been
# a member of each project stored on Codeplex before it was shut down
#
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

dbuser = ''
db = ''
dbhost = ''


# find all users on a project and their roles
# write the user/project/role to database
def parseAndInsertRole(roleid, role, projectName, div):
    listOfPeople = div.find("div", id=roleid)
    roleText = listOfPeople.find_all('div', {'class': 'UserDetails'})
    for r in roleText:
        username = r.find('a').contents[0]
        parseAndInsertUser(username)

        roleLine = r.find('div', {'class': 'SubText'})
        memberSinceLine = roleLine.find("span").contents[0]
        memberSince = convertDate(memberSinceLine)
        try:
            cursor.execute(insertRolesQuery, (projectName,
                                              datasourceID,
                                              username,
                                              role,
                                              memberSince))
            dbconn.commit()
        except pymysql.Error as error:
            print(error)
            dbconn.rollback()
    return


# collects and inserts information on user to users table
# checks first to see if we already have that user
def parseAndInsertUser(username):
    print("    checking on user:", username)

    # check to see if user is already in database
    userExists = None
    memberSince = None
    lastVisit = None
    statement = None
    try:
        cursor2.execute(selectUserQuery, (datasourceID, username))
        userExists = cursor2.fetchall()
    except pymysql.Error as error:
        print('database error:', error)
    except:
        print('unknown error')
        print(sys.exc_info()[0])
        raise

    if userExists:
        print('skipping user, already in cp_project_people')
    else:
        # get user's html page
        userUrl = 'http://www.codeplex.com/site/users/view/' + username
        print('    fetching user', username)

        try:
            req2 = urllib2.Request(userUrl, headers=hdr)
            userhtml = urllib2.urlopen(req2).read()

            soup2 = BeautifulSoup(userhtml, 'html.parser')
            dates = soup2.find('div', id='user_left_column')

            # get date user became a member
            try:
                memberSinceList = dates.find('p').contents[1].contents[0]
                memberSince = convertDate(memberSinceList)
                print('    --memberSince: ', memberSince)
            except:
                memberSince = None

            # get the last time the user visited
            try:
                lastVisitList = dates.find("p").contents[5].contents[0]
                lastVisit = convertDate(lastVisitList)
                print('    --lastVisit: ', lastVisit)
            except:
                lastVisit = None

            # get the user personal statement
            try:
                personal = soup2.find('div', id='user_right_column')
                s = personal.find('div', {'class': 'wikidoc'}).contents
                statement = ''.join(str(e) for e in s)
            except:
                statement = 'No personal statement has been written.'
            print('    --statement:', statement)

            try:
                cursor2.execute(insertHTMLQuery, (datasourceID,
                                                  username,
                                                  statement,
                                                  memberSince,
                                                  lastVisit,
                                                  userhtml))
                dbconn.commit()
                print(username, "inserted!")
            except pymysql.Error as error:
                print(error)

        except urllib2.HTTPError as herror:
            print(herror)

        except:
            print()


# converts months into their number
def convertMonth(moName):
    shortMoName = moName[0:3]
    months = {'Jan': '01',
              'Feb': '02',
              'Mar': '03',
              'Apr': '04',
              'May': '05',
              'Jun': '06',
              'Jul': '07',
              'Aug': '08',
              'Sep': '09',
              'Oct': '10',
              'Nov': '11',
              'Dec': '12'}
    # print(months[shortMoName])
    return months[shortMoName]


# converts date to YYYY-MM-DD format
def convertDate(listName):
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
cursor2 = dbconn.cursor()

selectProjectsQuery = 'SELECT proj_name \
                       FROM cp_projects_indexes \
                       WHERE datasource_id = %s'

selectPeopleIndexes = 'SELECT people_html \
                       FROM cp_projects_indexes \
                       WHERE datasource_id = %s \
                       AND proj_name = %s'

selectUserQuery = 'SELECT username \
                   FROM cp_project_people \
                   WHERE datasource_id = %s \
                   AND username = %s'

insertHTMLQuery = 'INSERT IGNORE INTO cp_project_people (datasource_id,\
                                                         username,\
                                                         personal_statement,\
                                                         member_since,\
                                                         last_visit,\
                                                         user_html,\
                                                         last_updated) \
                   VALUES (%s, %s, %s, %s, %s, %s, now())'

insertRolesQuery = 'INSERT INTO cp_project_people_roles (proj_name,\
                                                    datasource_id, \
                                                    username, \
                                                    role, \
                                                    project_member_since, \
                                                    last_updated) \
                  VALUES(%s, %s, %s, %s, %s, now())'

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
    cursor.execute(selectPeopleIndexes, (datasourceID, projectName))
    peopleHtml = cursor.fetchone()[0]
    if peopleHtml:
        try:
            soup = BeautifulSoup(peopleHtml, "html.parser")
            div = soup.find('div', id='ProjectMembers')

            # Get all of the Coordinators, Developers, Editors
            parseAndInsertRole("CoordinatorsContainer", "Coordinator", projectName, div)
            parseAndInsertRole("DevelopersContainer", "Developer", projectName, div)
            parseAndInsertRole("EditorsContainer", "Editor", projectName, div)

        except:
            print()
    else:
        print('  no people, skipping')
dbconn.close()
