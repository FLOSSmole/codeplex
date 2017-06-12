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
# 5parseCodeplexHistory.py <datasource_id> <db password>

# purpose:
# parse history pages for projects stored on Codeplex before it was shut down
################################################################

import pymysql
from bs4 import BeautifulSoup
import sys

datasourceID = sys.argv[1]
password     = sys.argv[2]

page_name = None
page_url = None
author = None
author_url = None

# Open remote database connection
dbconn = pymysql.connect(host='',
                         user='',
                         passwd=password,
                         db='codeplex',
                         use_unicode=True,
                         charset='utf8mb4',
                         autocommit=True)
cursor = dbconn.cursor()

selectProjects = 'SELECT proj_name \
                  FROM cp_projects_indexes \
                  WHERE datasource_id = %s'

selectIndex = 'SELECT history_html \
                 FROM cp_projects_indexes \
                 WHERE datasource_id = %s \
                 AND proj_name = %s'

insertProjectHistory = 'INSERT INTO cp_project_history (history_id, \
                                                  proj_name, \
                                                  datasource_id, \
                                                  month, \
                                                  year, \
                                                  page_name, \
                                                  page_url, \
                                                  author, \
                                                  author_url, \
                                                  last_updated) \
                        VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, now())'


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

# grab the project list
print('Selecting projects...')
cursor.execute(selectProjects, (datasourceID,))
projectList = cursor.fetchall()

for project in projectList:
    projectName = project[0]
    print("parsing project:", projectName)

    # grab the history page
    cursor.execute(selectIndex, (datasourceID, projectName))
    historyHtml = cursor.fetchone()[0]

    soup = BeautifulSoup(historyHtml, "html.parser")
    divs = soup.find_all("div", id="DateDiv")

    if divs:
        for d in divs:
            # get the h2 contents containing date information
            dateList = d.h2.contents
            # get dates and separate them by month and year
            for l in dateList:
                dateSplit = l.split(",")
                monthName = dateSplit[0]
                year = dateSplit[1]

                # to-do: convert month to 2-digit character
                monthNum = convertMonth(monthName)
                # get information on  user and page information for each update
                authorWholeList = d.find_all('tr')

                i = 0
                for line in authorWholeList:
                    authorList = line.find('td')

                    if authorList:
                        for section in authorList:
                            # get the author name and author url
                            author = line.find(id=('ModifiedByLiteral' +
                                                   str(i))).contents[0]
                            authorUrl = line.find(id=('ModifiedByLiteral' +
                                                      str(i)))['href']
                            # get the page name and page url
                            page = line.find(id=('PageTitleLink' +
                                                 str(i))).contents[0]
                            pageUrl = line.find(id=('PageTitleLink' +
                                                    str(i)))['href']
                            cursor.execute(insertProjectHistory, (projectName,
                                                                  datasourceID,
                                                                  monthNum,
                                                                  year,
                                                                  page,
                                                                  pageUrl,
                                                                  author,
                                                                  authorUrl))
                            i += 1
dbconn.close()
