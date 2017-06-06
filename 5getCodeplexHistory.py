#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it
# and/or modify it under the terms of GPL v3
#
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# Contribution from:
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
# 1getCodeplexPages.py <datasource_id> <db password>

# purpose:
# grab all the authors, author urls, pages, and page url of page updates for projects stored on Codeplex before it was shut down
################################################################

import pymysql
from bs4 import BeautifulSoup
import sys
import getpass
import datetime
import re

pw=getpass.getpass()

# grab commandline args
datasourceID = 70910 
last_updated = None

page_name = None
page_url = None
author = None
author_url= None

# Open remote database connection
dbconn = pymysql.connect(host='',
                         user='',
                         passwd=pw,
                         db='',
                         use_unicode=True,
                         charset="utf8mb4",
                         autocommit=True)
cursor = dbconn.cursor()


selectProjects = 'SELECT proj_name \
                  FROM cp_projects_indexes \
                  WHERE datasource_id = %s'
                  
selectIndexes = 'SELECT history_html \
                 FROM cp_projects_indexes \
                 WHERE datasource_id = %s \
                 AND proj_name = %s' 
                 
insertProjects = 'INSERT INTO cp_project_historyC \
                  values(NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s)'            
             

# grab the project list
cursor.execute(selectProjects, (datasourceID,))
projectList = cursor.fetchall()


for project in projectList:
    projectName = project[0]
    print("parsing:", projectName)
    
    # grab the index
    cursor.execute(selectIndexes, (datasourceID, projectName))
    historyHtml = cursor.fetchone()[0]

    #grab the history page we need 
    soup = BeautifulSoup(historyHtml, "html.parser")
    divs = soup.find_all("div", id="DateDiv")

    if divs:
        for d in divs:
            # get the h2 contents that contain information on the date of updates 
            dateList = d.h2.contents
            # get dates and separate them by month and year
            for l in dateList:
                date = l
                dateSplit = l.split(",")
                month = dateSplit[0]
                year = dateSplit[1]
                
                #gets information on  user and page informaiton for each update
                authorWholeList = d.find_all('tr')

                i=0
                for line in authorWholeList:
                    authorList = line.find('td')

                    if authorList:
                        for section in authorList:
                            # get the author name and author url
                            author = line.find(id=('ModifiedByLiteral' + str(i))).contents[0]
                            authorUrl = line.find(id=('ModifiedByLiteral' + str(i)))['href']
                            
                            # get the page name and page url
                            page = line.find(id=('PageTitleLink' + str(i))).contents[0]
                            pageUrl = line.find(id=('PageTitleLink' + str(i)))['href']

                            i = i+1  
                            last_updated = datetime.datetime.now()
                            
                            cursor.execute(insertProjects, (projectName, datasourceID, month, year, page, pageUrl, author, authorUrl, last_updated))
dbconn.close()
