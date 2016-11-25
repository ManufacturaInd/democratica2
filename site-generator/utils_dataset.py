#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
import unicodecsv as csv
import json
import glob
import mistune
import datetime
from dateutil import parser as dateparser
from collections import OrderedDict
from utils import slugify

MP_DATASET_FILE = os.path.expanduser("~/datasets-central/parlamento-deputados/data/deputados.json")
MPINFO_DATASET_FILE = os.path.expanduser("~/datasets-central/parlamento-deputados/data/deputados-extra.csv")
GOV_DATASET_FILE = os.path.expanduser("~/datasets-central/governos/data/governos-pm.csv")
GOVPOST_DATASET_FILE = os.path.expanduser("~/datasets-central/governos/data/governos-cargos.csv")
TRANSCRIPTS_DIR = os.path.expanduser("~/datasets/dar-transcricoes-txt/data/")
TRANSCRIPT_DATASET_FILE = os.path.expanduser("~/datasets-central/parlamento-datas_sessoes/data/datas-debates.csv")
TRANSCRIPT_DATASET_FILE_2 = os.path.expanduser("~/datasets-central/parlamento-datas_sessoes/data/datas-parlamento.csv")


def get_date_dataset():
    data = csv.reader(open(TRANSCRIPT_DATASET_FILE, 'r'))
    # skip first row
    data.next()

    more_data = csv.reader(open(TRANSCRIPT_DATASET_FILE_2, 'r'))
    # skip first row
    more_data.next()

    data = list(data)

    for newrow in more_data:
        exists = False
        leg, sess, num = newrow[:3]
        for row in data:
            if row[:3] == [leg, sess, num]:
                exists = True
                break
        if not exists:
            data.append(newrow)
            # print newrow

    return data


def get_gov_dataset():
    data = csv.reader(open(GOV_DATASET_FILE, 'r'))
    # skip first row
    data.next()
    return list(data)


def get_mp_dataset():
    data = json.loads(open(MP_DATASET_FILE, 'r').read())
    info_data = csv.reader(open(MPINFO_DATASET_FILE, 'r'))
    info_data.next()
    for row in info_data:
        mp = data[row[0]]
        mp['email'] = row[3]
        mp['wikipedia_url'] = row[4]
        mp['twitter_url'] = row[6]
        mp['blog_url'] = row[7]
        mp['website_url'] = row[8]
    return data


def get_govpost_dataset():
    data = csv.reader(open(GOVPOST_DATASET_FILE, 'r'))
    # skip first row
    data.next()
    return list(data)


def generate_datedict():
    # process dates into a year->dates dict
    datedict = OrderedDict()
    data = get_date_dataset()
    all_dates = [dateparser.parse(row[3]) for row in data]
    all_years = list(set([d.year for d in all_dates]))
    for year in all_years:
        # populate it with its months
        # if current year, trim future months
        if int(year) == datetime.date.today().year:
            month = datetime.date.today().month
            months = range(1, month + 1)
        else:
            months = range(1, 13)
        datedict[year] = {}
        for month in months:
            datedict[year][month] = {}
            import calendar
            days_in_month = calendar.monthrange(year, month)[-1]
            all_days = range(1, days_in_month + 1)
            session_days = [datetime.date(d.year, d.month, d.day) for d in all_dates
                            if d.month == month and d.year == year]
            for day_number in all_days:
                day_date = datetime.date(year, month, day_number)
                if day_date in session_days:
                    has_session = True
                else:
                    has_session = False
                datedict[year][month][day_number] = {'weekday': day_date.weekday(),
                                                     'has_session': has_session}
    return datedict


def generate_mp_list(only_active=True):
    mps = []
    data = get_mp_dataset()
    for id in data:
        mp = data[id]
        if only_active and not mp['active']:
            continue
        mp['slug'] = slugify(mp['shortname'])
        if 'occupation' in mp and len(mp['occupation']) == 1:
            mp['occupation'] = mp['occupation'][0]
        mps.append(mp)
    return mps


def get_mp_from_shortname(shortname):
    mps = generate_mp_list()
    mp = filter(lambda x: x['shortname'] == shortname, mps)[0]
    return mp


def get_session_contents(leg, sess, num):
    if 'S' in num:
        fnstart = "%02d-%d-%s" % (int(leg), int(sess), num)
    else:
        fnstart = "%02d-%d-%03d" % (int(leg), int(sess), int(num))
    # encontrar .txt ou .json
    files = glob.glob(os.path.join(TRANSCRIPTS_DIR, fnstart) + '*')
    if not files:
        return None
    fn = files[0]
    text = codecs.open(fn, 'r', 'utf-8').read()
    if fn.endswith('.json'):
        return json.loads(text)
    elif fn.endswith('.txt'):
        entries = text.split('\n\n')
        newentries = []
        for e in entries:
            # adicionar linebreak extra para dividir parágrafos
            newentries.append(e.replace('\n', '\n\n'))
        newtext = "\n\n".join(newentries)
        newhtml = mistune.markdown(newtext)
        return newhtml.replace("_", "")
    else:
        return text


def get_session_info(leg, sess, num):
    if 'S' in num:
        fnstart = "%02d-%d-%s" % (int(leg), int(sess), num)
    else:
        fnstart = "%02d-%d-%03d" % (int(leg), int(sess), int(num))
    files = glob.glob(os.path.join(TRANSCRIPTS_DIR, fnstart) + '*.json')
    if not files:
        return None
    fn = files[0]
    text = codecs.open(fn, 'r', 'utf-8').read()
    data = json.loads(text)
    del data['contents']
    return data
