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

TRANSCRIPTS_DIR = os.path.expanduser("~/datasets/dar-transcricoes-txt/data/")
TRANSCRIPT_DATASET_FILE = os.path.expanduser("~/datasets-central/parlamento-datas_sessoes/data/datas-debates-novo.csv")
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


def generate_datedict():
    '''
    Creates a dict with details for every day:
    * which weekday it is
    * whether there was a session on that day

    It's laid out in year - month - day - details order.
    Example:
    OrderedDict([(1976, {1: {1: {'weekday': 3, 'has_session': False}, 2: {'weekday': 4, 'has_session': False}, 3: {'weekday': 5, 'has_session': False}, .....
    '''
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
                if has_session:
                    session_glob = TRANSCRIPTS_DIR + "/*_%d-%02d-%02d.json" % (year, month, day_number)
                    if glob.glob(session_glob):
                        # sacar a topword
                        s = json.loads(open(glob.glob(session_glob)[0], 'r').read())
                        if 'stats' in s:
                            topword = s['stats']['topwords']['session'][0][0]
                            datedict[year][month][day_number]['topword'] = topword
    return datedict


def get_session_from_legsessnum(leg, sess, num):
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


# FIXME: Duplicate code from darparser

MP_DATASET_FILE = os.path.expanduser("~/datasets-central/parlamento-deputados/data/deputados.json")
MPINFO_DATASET_FILE = os.path.expanduser("~/datasets-central/parlamento-deputados/data/deputados-extra.csv")
GOV_DATASET_FILE = os.path.expanduser("~/datasets-central/governos/data/governos-pm.csv")
GOVPOST_DATASET_FILE = os.path.expanduser("~/datasets-central/governos/data/governos-cargos.csv")


def get_mp_dataset():
    data = json.loads(open(MP_DATASET_FILE, 'r').read())
    info_data = csv.reader(open(MPINFO_DATASET_FILE, 'r'))
    info_data.next()
    for row in info_data:
        mp = data[row[1]]
        mp['email'] = row[3]
        mp['wikipedia_url'] = row[4]
        mp['twitter_url'] = row[6]
        mp['blog_url'] = row[7]
        mp['website_url'] = row[8]
    return data


def get_gov_dataset():
    data = csv.reader(open(GOV_DATASET_FILE, 'r'))
    # skip first row
    data.next()
    return list(data)


def get_govpost_dataset():
    data = csv.reader(open(GOVPOST_DATASET_FILE, 'r'))
    # skip first row
    data.next()
    return list(data)


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

mp_data = generate_mp_list(only_active=False)


def get_mp_from_shortname(shortname, leg=None):
    results = filter(lambda x: x['shortname'] == shortname, mp_data)
    mp = None
    if len(results) == 0:
        log.error("No MP results for shortname %s" % shortname.encode('utf-8'))
        return None
    elif len(results) > 1:
        if leg:
            # vários resultados - ver qual deles tem mandato nesta legislatura
            leg_mps = []
            for r in results:
                for m in r['mandates']:
                    if m['legislature'] == leg:
                        leg_mps.append(r)
                        continue
            if len(leg_mps) == 1:
                mp = leg_mps[0]
            else:
                log.error("Multiple MP results for shortname %s: %s" % (shortname, ", ".join([mp['shortname'] for mp in results])))
        else:
            log.error("Multiple MP results for shortname %s: %s" % (shortname, ", ".join([mp['shortname'] for mp in results])))
        mp = results[0]
    if mp:
        del mp['mandates']
        del mp['commissions']
        if 'jobs' in mp:
            del mp['jobs']
        if 'education' in mp:
            del mp['education']
        if 'awards' in mp:
            del mp['awards']
    return mp


def get_mp_from_id(id):
    results = filter(lambda x: x['id'] == int(id), mp_data)
    if len(results) == 0:
        log.error("No MP results for id %d" % id)
        return None
    elif len(results) > 1:
        log.error("Multiple MP results for id %d: %s" % (id, ", ".join(results)))
        return results[0]
    return results[0]
