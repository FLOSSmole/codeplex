# -*- coding: utf-8 -*-
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# License: GPLv3
# 
# Contribution from:
# Caroline Frankel
#
# We're working on this at http://flossmole.org - Come help us build
# an open and accessible repository for data and analyses for free and open
# source projects.
#
# If you use this code or data for preparing an academic paper please
# provide a citation to:
#
# Howison, J., Conklin, M., & Crowston, K. (2006). FLOSSmole:
# A collaborative repository for FLOSS research data and analyses.
# International Journal of Information Technology and Web Engineering, 1(3),
# 17–26.
#
# and
#
# FLOSSmole: a project to provide research access to
# data and analyses of open source projects.
# Available at http://flossmole.org
#
################################################################
# usage:
# python 6LaunchpadParserBugTagTable.py <datasource_id> <password>
#
# purpose:
# inserts bug tag information into the bug tag table
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup

datasource_id = '122'  # sys.argv[1]


def run():
    try:
        cursor.execute(insertBugTagQuery,
                       (datasource_id,
                        name, 
                        official_bug_tag))
        db.commit()
        print(name, " inserted into bug tag table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()     

# establish database connection: SYR
try:
    db = pymysql.connect(host='flossdata.syr.edu',
                     user='',
                     passwd='',
                     db='',
                     use_unicode=True,
                     charset="utf8mb4")
    cursor = db.cursor()
except pymysql.Error as err:
    print(err)

selectQuery = 'SELECT name, html FROM lpd_indexes'


insertBugTagQuery = 'INSERT INTO lpd_official_bug_tags (datasource_id, \
                                                          name, \
                                                          official_bug_tag, \
                                                          last_updated) \
                       VALUES(%s, %s, %s, now())'

try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        name = project[0]
        html = project[1]
        print('\nworking on ', name)

        soup = BeautifulSoup(html, 'html.parser')

        regex = '\"official_bug_tags\": \[(.*?)\]'
        listOfTags = re.findall(regex, str(soup))
        if listOfTags:
            splitList = listOfTags[0].split(',')
            for s in splitList:
                regex2 = '"(.*?)"'
                word = re.findall(regex2, str(s))
                if word:
                    official_bug_tag = word[0]
                    print('official_bug_tag: ', official_bug_tag)
                    run()

except pymysql.Error as err:
    print(err)
