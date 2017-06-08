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
# 1getCodeplexPages.py <datasource_id> <db password>

# purpose:
# grab all the projects, contributors, their role, and how long they have been a member of each project stored on Codeplex before it was shut down
################################################################

import pymysql
import datetime
from bs4 import BeautifulSoup

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

# grab commandline args
datasourceID = 70910 
lastUpdated = None

# converts months into their number
def month_converter(month):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months.index(month) + 1

# converts date to YYYY-MM-DD format
def date_converter(lineName):
    memberSinceLine = lineName.find("span").contents[0]
    date = memberSinceLine.split(' ')
    month = date[0]
    day = date[1].split(',')[0]
    year = date[2] 
    monthNum = month_converter(month)
    return '{}-{}-{}'.format(year, monthNum, day)  

# runs the program
def run():
    lastUpdated = datetime.datetime.now()
    cursor.execute(insertQuery, (projectName, datasourceID, username, role, memberSince, lastUpdated))
    dbconn.commit()
    
# Open remote database connection
dbconn = pymysql.connect(host='',
                         user='',
                         passwd=pw,
                         db='',
                         use_unicode=True,
                         charset="utf8mb4",
                         autocommit=True)
cursor = dbconn.cursor()

selectProjectsQuery = 'SELECT proj_name FROM cp_projects_indexes \
                       WHERE datasource_id = %s \
                       ORDER BY 1 \
                       LIMIT 100'

insertQuery = 'INSERT INTO cp_project_people_roles \
                  values(%s, %s, %s, %s, %s, %s)'  

cursor.execute(selectProjectsQuery, (datasourceID,))
projectList = cursor.fetchall()
    
# insert project pages
for project in projectList:
    projectName = project[0] 
    print("grabbing", projectName)

    # set up headers
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
 
    try:
        # grab the project page
        projectUrl = 'http://' + projectName + '.codeplex.com/team/view'
        req = urllib2.Request(projectUrl, headers=hdr)
        projecthtml = urllib2.urlopen(req).read()

        soup = BeautifulSoup(projecthtml, "html.parser")
        div = soup.find("div", id="ProjectMembers")     
  
        # Get all of the Coordinators 
        listOfCoordinators = div.find("div", id="CoordinatorsContainer")
        coordinatorLine = listOfCoordinators.find_all('div', {'class': 'UserDetails'})

        for coordinator in coordinatorLine:
           username = coordinator.find('a').contents[0]
           role = 'Coordinator'
           coordinatorLine = coordinator.find('div', {'class': 'SubText'})
           memberSince = date_converter(coordinatorLine)
           run()

        # Get all of the Developers 
        listOfDevelopers = div.find("div", id="DevelopersContainer")
        developerLine = listOfDevelopers.find_all('div', {'class': 'UserDetails'})

        for developer in developerLine:
           username = developer.find('a').contents[0]
           role = 'Developer'
           developerLine = developer.find('div', {'class': 'SubText'})
           memberSince = date_converter(developerLine)
           run()

        # Get all of the Editors           
        listOfEditors = div.find("div", id="EditorsContainer")
        editorLine = listOfEditors.find_all('div', {'class': 'UserDetails'})

        for editor in editorLine:
           username = editor.find('a').contents[0]
           role = 'Editor'
           editorLine = editor.find('div', {'class': 'SubText'})
           memberSince = date_converter(editorLine)
           run()
    
    except pymysql.Error as error:
        print(error)
        dbconn.rollback()
    except:
        print()
        
dbconn.close()
