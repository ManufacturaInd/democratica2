#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
from datetime import date
from dateutil import parser as dateparser
import os
import codecs
import shutil
import markdown
from zenlog import log

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

DATASETS_DIR = "~/Datasets/"
OUTPUT_DIR = "_output"
MEDIA_SOURCE_DIR = "_media"

###################
# 1. PREPARE DATA #
###################

DATASETS_DIR = os.path.expanduser(DATASETS_DIR)
# fetch all dates
data = csv.reader(open(os.path.join(DATASETS_DIR, 'dar-datas.csv'), 'r'))
# skip header
data.next()
# process dates into a year->dates dict
all_dates = [dateparser.parse(row[3]) for row in data]
all_years = list(set([d.year for d in all_dates]))

datedict = {}
for year in all_years:
    # populate it with its months
    # if current year, trim future months
    if int(year) == date.today().year:
        month = date.today().month
        months = range(1, month+1)
    else:
        months = range(1, 13)
    datedict[year] = {}
    for month in months:
        datedict[year][month] = {}
        import calendar
        days_in_month = calendar.monthrange(year, month)[-1]
        all_days = range(1, days_in_month+1)
        session_days = [date(d.year, d.month, d.day) for d in all_dates
                        if d.month == month and d.year == year]
        for day_number in all_days:
            day_date = date(year, month, day_number)
            if day_date in session_days:
                has_session = True
            else:
                has_session = False
            datedict[year][month][day_number] = {'weekday': day_date.weekday(),
                                                 'has_session': has_session}

##########################
# 2. GENERATE HTML FILES #
##########################

# flush output dir
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.mkdir(OUTPUT_DIR)

# init Jinja
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('democratica', 'templates'),
                  extensions=['jinja2htmlcompress.SelectiveHTMLCompress'],
                  trim_blocks=True, lstrip_blocks=True)

# HOME PAGE #

template = env.get_template('index.html')
html = template.render()
filename = "index.html"
outfile = codecs.open(os.path.join(OUTPUT_DIR, filename), 'w', 'utf-8')
outfile.write(html)
outfile.close()
log.debug("%s created OK" % filename)

# SESSION CALENDAR #

log.info("Generating session calendar...")
template = env.get_template('transcripts/day_list.html')
for year_number in datedict:
    year = datedict[year_number]
    context = {'year': year,
               'year_number': year_number,
               'datedict': datedict,
               }
    html = template.render(**context)
    filename = "%s.html" % year_number
    outfile = codecs.open(os.path.join(OUTPUT_DIR, filename), 'w', 'utf-8')
    outfile.write(html)
    outfile.close()
    # log.debug("%s created OK" % filename)

# STATIC FILES #

log.info("Regenerating static files...")
# regenerate static content dir (css, js, images, fonts)
media_path = os.path.join(OUTPUT_DIR, 'media')
if os.path.exists(media_path):
    shutil.rmtree(media_path)
os.mkdir(media_path)
# copy_tree method lifted from http://stackoverflow.com/a/15034373
import distutils.core
distutils.dir_util.copy_tree(MEDIA_SOURCE_DIR, media_path)

# INDIVIDUAL SESSIONS #

template = env.get_template('transcripts/day_detail_markdown.html')
log.info("Generating HTML session pages...")
sessions_dir = "sessoes/"
os.mkdir(os.path.join(OUTPUT_DIR, sessions_dir))
# fetch all dates
data = csv.reader(open(os.path.join(DATASETS_DIR, 'dar-datas.csv'), 'r'))
# skip header
data.next()
for leg, sess, num, d, dpub in data:
    filename = d + '.html'
    if 'S' in num:
        sourcefile = "%02d-%d-%s.txt" % (int(leg), int(sess), num)
    else:
        sourcefile = "%02d-%d-%03d.txt" % (int(leg), int(sess), int(num))
    sourcepath = os.path.join(
        (DATASETS_DIR), 'dar-transcricoes-txt', sourcefile)
    text = codecs.open(sourcepath, 'r', 'utf-8').read()
    html_text = markdown.markdown(text)
    context = {'session_date': dateparser.parse(d),
               'year_number': year_number,
               'text': html_text,
               'pdf_url': 'xpto',
               }
    html = template.render(**context)
    outfile = codecs.open(os.path.join(OUTPUT_DIR, filename), 'w', 'utf-8')
    outfile.write(html)
    outfile.close()
    log.debug(filename)

    # sourcepath = os.path.join(DATASETS_DIR,
    #                          "dar-transcricoes-html/", sourcefile)
    # targetpath = os.path.join(OUTPUT_DIR, sessions_dir, filename)
    # shutil.copyfile(sourcepath, targetpath)


