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
# Create a bar graph that shows 100 Codeplex Pojects with the largest number of contributors
################################################################

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pymysql


datasourceID = 70910 

# Open remote database connection
dbconn = pymysql.connect(host='',
                         user='',
                         passwd=pw,
                         db='',
                         use_unicode=True,
                         charset="utf8mb4",
                         autocommit=True)
cursor = dbconn.cursor()

# get the project name and the amount of contributors in each project for the 100 projects with the highest contributors
selectProjectsQuery = 'SELECT proj_name, COUNT(proj_name) \
                            FROM cp_project_people_roles \
                            WHERE datasource_id = %s \
                            GROUP BY 1 \
                            ORDER BY COUNT(proj_name)  DESC\
                            LIMIT 100'

cursor.execute(selectProjectsQuery, (datasourceID,))
projectList = cursor.fetchall()
names = []
x=0

# for each project, plot it on the bar graph
for project in projectList:
    labels = names.append(project[0])
    data = project[1]

    x=x+1
    y = project[1]
    plt.bar(x,y, color='c')
    plt.xticks(range(0,100), names,rotation ='vertical', fontsize=12)
    
    plt.xlabel('Project Name')
    plt.ylabel('Number of Contributors')
    plt.title('100 Codeplex Projects with the largest number of Contributors ')
    plt.show()
