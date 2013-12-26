#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib2
import json
from datetime import date
from pprint import pprint
import os, shutil

MESES = [
    'Janeiro',
    'Fevereiro',
    'Março',
    'Abril',
    'Maio',
    'Junho',
    'Julho',
    'Agosto',
    'Setembro',
    'Outubro',
    'Novembro',
    'Dezembro',
    ]

VIEW_URL = "http://koizo.org:5984/dar-1_datas/_design/dar/_view/all_dates"
OUTPUT_DIR = "_output"
MEDIA_SOURCE_DIR = "_media"

# fetch all dates
page = urllib2.urlopen(VIEW_URL)
data = json.loads(page.read())

rows = data['rows']

# process dates into a year->dates dict
from dateutil import parser
all_dates = [parser.parse(row['key']) for row in rows]
all_years = list(set([d.year for d in all_dates]))

datedict = {}
for year in all_years:
    # populate it with its months
    # if current year, trim future months
    if int(year) == date.today().year:
        month = date.today().month
        months = range(1, month+1)
    else:
        months = range(1,13)
    datedict[year] = {}
    for month in months:
        datedict[year][month] = {}
        import calendar
        days_in_month = calendar.monthrange(year, month)[-1]
        all_days = range(1, days_in_month+1)
        session_days = [date(d.year, d.month, d.day) for d in all_dates if d.month == month and d.year == year]
        for day_number in all_days:
            day_date = date(year, month, day_number)
            if day_date in session_days:
                has_session = True
            else:
                has_session = False
            datedict[year][month][day_number] = {'weekday': day_date.weekday(),
                                                 'has_session': has_session}

# FIXME, this is stupid
all_years = datedict
# init Jinja
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('democratica', 'templates'),
                  extensions=['jinja2htmlcompress.SelectiveHTMLCompress'],
                  trim_blocks=True, lstrip_blocks=True)

# generate home page
template = env.get_template('index.html')
html = template.render()
filename = "index.html"
import os, codecs
outfile = codecs.open(os.path.join(OUTPUT_DIR, filename), 'w', 'utf-8')
outfile.write(html)
outfile.close()
print "%s created OK" % filename

# generate year indexes
template = env.get_template('transcripts/day_list.html')
for year_number in all_years:
    year = all_years[year_number]
    context = {'year': year,
               'year_number': year_number,
               'all_years': all_years,
               }
    html = template.render(**context)
    filename = "%s.html" % year_number
    import os, codecs
    outfile = codecs.open(os.path.join(OUTPUT_DIR, filename), 'w', 'utf-8')
    outfile.write(html)
    outfile.close()
    print "%s created OK" % filename
    
# replace static content (css, js, images, fonts)
media_path = os.path.join(OUTPUT_DIR, 'media')
if os.path.exists(media_path):
    shutil.rmtree(media_path)
os.mkdir(media_path)
# thank you SO user prosseek http://stackoverflow.com/a/15034373
import distutils.core
distutils.dir_util.copy_tree(MEDIA_SOURCE_DIR, media_path)

