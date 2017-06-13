#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it
# and/or modify it under the terms of GPL v3
#
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# Contributions from:
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
# 8getCodeplexLicenseNames.py <datasource_id> <db password>

# purpose:
# get the license names for Codeplex projects
################################################################

import sys
import pymysql
import getpass
import datetime
from bs4 import BeautifulSoup

try:
    import urllib.request as urllib2
except ImportError:
    import urllib2
codeplexDatasourceID = 70910
    # grab commandline args
datasourceID = codeplexDatasourceID
pw = getpass.getpass()

dbuser = 'jhartmann'
db = 'test'
dbhost = 'flossdata.syr.edu'

dbconn = pymysql.connect(host= dbhost,
                         user= dbuser,
                         passwd= pw,
                         db= db,
                         use_unicode=True,
                         charset="utf8mb4")
cursor = dbconn.cursor()

selectProjectsQuery = 'SELECT proj_name, proj_url FROM cp_projects\
                       WHERE datasource_id = %s \
                       ORDER BY 1'
                       
updateProjects = 'UPDATE cp_projects SET \
                  proj_license= %s, \
                  last_updated = %s \
                  WHERE proj_name = %s AND datasource_id = %s'
                  
cursor.execute(selectProjectsQuery, (datasourceID,))
projectList = cursor.fetchall()

#insert license name to projects
for project in projectList:
    projectName = project[0]
    projectUrl = project[1]
    print("grabbing     ", projectName)
    
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
   
    try:
       
        #grap the license page 
        licenseUrl = projectUrl + 'license'
        req = urllib2.Request(licenseUrl,headers=hdr)
        licenseHtml = urllib2.urlopen(req).read()
        
        #Parse the Html for license name
        if licenseHtml:         
            soup = BeautifulSoup(licenseHtml, 'html.parser')
            div = soup.find('div', id = 'left_column') 
            if div:
                license = div.h1.contents
                licenseName = license[0]
                print (licenseName)  
                current_time = datetime.datetime.now()
                cursor.execute(updateProjects, (licenseName, current_time, projectName, datasourceID))
                
                dbconn.commit()
                
                
    except pymysql.Error as error:
        print(error)
        dbconn.rollback()
        
    except:
        print('')
  

dbconn.close()           
   
