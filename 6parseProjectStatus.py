#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it
# and/or modify it under the terms of GPL v3
#
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# Contributions from:
# Caroline Frankel
# Jack Hartmann
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
# 6parseProjectStatus.py <datasource_id> <db password>

# purpose:
# parse the pages for Codeplex projects for project status
################################################################

import sys
import pymysql
import datetime
import re
import getpass
password = getpass.getpass()

datasourceID = 70910
lastUpdated = 'Null'

# Open remote database connection
dbconn = pymysql.connect(host= "",
                         user= "",
                         passwd=password,
                         db="",
                         use_unicode=True,
                         charset="utf8mb4",
                         autocommit=True)
cursor = dbconn.cursor()

selectProjects = 'SELECT proj_name \
                  FROM cp_projects_indexes \
                  WHERE datasource_id = %s'

selectIndexes = 'SELECT home_html \
                 FROM cp_projects_indexes \
                 WHERE datasource_id = %s \
                 AND proj_name = %s'      
                 
updateProjects = 'UPDATE cp_projects SET \
                  proj_status= %s, \
                  last_updated = %s \
                  WHERE proj_name = %s AND datasource_id = %s'
 
# grab the project list                  
cursor.execute(selectProjects, (datasourceID,))
projectList = cursor.fetchall()

for project in projectList:
    projectName = project[0]
    print("parsing:", projectName)
    
    #grab the index
    cursor.execute(selectIndexes, (datasourceID, projectName))
    homeHtml = cursor.fetchone()[0]
    
    regex = 'status<\/span><\/th>\s*<td>(.*?)<\/td'
    match = re.findall(regex, homeHtml)
    
    #parse out the project's most recent status
    if match:
        current_time = datetime.datetime.now()
        cursor.execute(updateProjects, (match[0], current_time, projectName, datasourceID))
   
dbconn.close()


                  
