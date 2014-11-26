#!/usr/bin/env python
# -*- coding: utf-8 -*-
import distutils.core
from distutils.dir_util import copy_tree
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
MEDIA_PATH = "media/"
TRANSCRIPTS_PATH = "sessoes/"


DATASETS_DIR = os.path.expanduser(DATASETS_DIR)


def get_date_dataset():
    data = csv.reader(open(os.path.join(DATASETS_DIR, 'dar-datas.csv'), 'r'))
    # skip first row
    data.next()
    return data


def generate_datedict():
    # process dates into a year->dates dict
    datedict = {}
    data = get_date_dataset()
    all_dates = [dateparser.parse(row[3]) for row in data]
    all_years = list(set([d.year for d in all_dates]))
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


def render_template_into_file(env, templatename, filename, context=None, place_in_outdir=True):
    template = env.get_template(templatename)
    if not context:
        context = {}
    html = template.render(**context)
    if place_in_outdir:
        filename = os.path.join(OUTPUT_DIR, filename)
    outfile = codecs.open(filename, 'w', 'utf-8')
    outfile.write(html)
    outfile.close()


def get_session_text(leg, sess, num, html=True):
    if 'S' in num:
        sourcefile = "%02d-%d-%s.txt" % (int(leg), int(sess), num)
    else:
        sourcefile = "%02d-%d-%03d.txt" % (int(leg), int(sess), int(num))
    sourcepath = os.path.join(
        (DATASETS_DIR), 'dar-transcricoes-txt', sourcefile)
    text = codecs.open(sourcepath, 'r', 'utf-8').read()
    if html:
        return markdown.markdown(text)
    else:
        return text


def delete_and_create_dir(d):
    """Deletes a directory if it exists, and creates a new one with the
    same name."""
    if os.path.exists(d):
        shutil.rmtree(d)
    os.mkdir(d)


def generate_site():
    # flush output
    delete_and_create_dir(OUTPUT_DIR)
    delete_and_create_dir(os.path.join(OUTPUT_DIR, TRANSCRIPTS_PATH))
    delete_and_create_dir(os.path.join(OUTPUT_DIR, MEDIA_PATH))

    # init Jinja
    from jinja2 import Environment, PackageLoader
    env = Environment(loader=PackageLoader('democratica', 'templates'),
                      extensions=['jinja2htmlcompress.SelectiveHTMLCompress'],
                      trim_blocks=True, lstrip_blocks=True)

    # generate pages
    log.info("Generating index...")
    render_template_into_file(env, 'index.html', 'index.html')

    log.info("Generating session calendar...")
    datedict = generate_datedict()
    for year_number in datedict:
        year = datedict[year_number]
        context = {'year': year,
                   'year_number': year_number,
                   'datedict': datedict,
                   }
        filename = "%s.html" % year_number
        render_template_into_file(env, 'transcripts/day_list.html', filename, context)

    log.info("Generating HTML session pages...")
    data = csv.reader(open(os.path.join(DATASETS_DIR, 'dar-datas.csv'), 'r'))
    data.next()
    for leg, sess, num, d, dpub in data:
        context = {'session_date': dateparser.parse(d),
                   'year_number': year_number,
                   'text': get_session_text(leg, sess, num),
                   'pdf_url': 'xpto',
                   }
        render_template_into_file(env, 'transcripts/day_detail_markdown.html', d + '.html', context)
        log.debug(filename)

    log.info("Copying static files...")
    copy_tree(MEDIA_SOURCE_DIR, MEDIA_PATH)

if __name__ == "__main__":
    generate_site()
