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
# grab all the user htmls from Codeplex before it was shut down
################################################################

import pymysql
import datetime

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

# grab commandline args
datasourceID = 70910 
lastUpdated = None


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
                       LIMIT 20'

updateHTMLQuery = 'UPDATE cp_projects_indexes \
                        SET people_html = %s, last_updated = %s \
                        WHERE proj_name = %s AND datasource_id = 70910' 

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
        # grab the user page
        peopleUrl = 'http://' + projectName + '.codeplex.com/team/view'
        print(peopleUrl)
        req = urllib2.Request(peopleUrl, headers=hdr)
        peoplehtml = urllib2.urlopen(req).read()
        print(peoplehtml)
        
        lastUpdated = datetime.datetime.now()
        cursor.execute(updateHTMLQuery, (peoplehtml,lastUpdated, projectName))
        dbconn.commit()
    except pymysql.Error as error:
        print(error)
        dbconn.rollback()
    except:
        print()
        
dbconn.close()





















