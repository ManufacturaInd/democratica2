#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
import unicodecsv as csv
import json
import hoep
import datetime
from collections import OrderedDict
from utils import slugify, parse_iso_date

TRANSCRIPTS_DIR = os.path.expanduser("~/datasets/dar-transcricoes-txt/data/")
TRANSCRIPT_DATASET_FILE = os.path.expanduser("~/datasets-central/parlamento-datas_sessoes/data/datas-debates-novo.csv")


def get_date_dataset():
    data = csv.reader(open(TRANSCRIPT_DATASET_FILE, 'r'))
    # skip first row
    data.next()
    data = list(data)
    return data


datedata = get_date_dataset()
markdown = hoep.Hoep()


def get_session_filename_from_number(leg, sess, num):
    session = None
    for row in datedata:
        if row[0] == str(leg) and row[1] == str(sess) and row[2] == str(num):
            session = row
            break
    if not session:
        print("No database match for legsessnum %d %d %d" % (leg, sess, num))
        return None
    datestring = session[3]
    leg = int(leg)
    sess = int(sess)
    try:
        num = int(num)
        json_filename = os.path.join(TRANSCRIPTS_DIR, '%02d-%d-%03d_%s.json' % (leg, sess, num, datestring))
        txt_filename = os.path.join(TRANSCRIPTS_DIR, '%02d-%d-%03d.txt' % (leg, sess, num))
    except ValueError:
        # número tem uma letra no nome (ex. "136S1")
        json_filename = os.path.join(TRANSCRIPTS_DIR, '%02d-%d-%s_%s.json' % (leg, sess, num, datestring))
        txt_filename = os.path.join(TRANSCRIPTS_DIR, '%02d-%d-%s.txt' % (leg, sess, num))

    if os.path.exists(json_filename):
        return json_filename
    elif os.path.exists(txt_filename):
        return txt_filename
    else:
        return None


def get_session_filename_from_date(dateobj):
    datestring = "%d-%02d-%02d" % (dateobj.year, dateobj.month, dateobj.day)
    for row in datedata:
        if row[3] == datestring:
            session = row
            break
    if not session:
        print("No database match for date %s" % (datestring))
        return None
    leg, sess, num = session[:3]
    json_filename = os.path.join(TRANSCRIPTS_DIR, '%02d-%d-%03d_%s.json' % (int(leg), int(sess), int(num), datestring))
    txt_filename = os.path.join(TRANSCRIPTS_DIR, '%02d-%d-%03d.txt' % (int(leg), int(sess), int(num)))
    if os.path.exists(json_filename):
        return json_filename
    elif os.path.exists(txt_filename):
        return txt_filename
    else:
        return None
    pass


def generate_datedict(fast_run=False):
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
    all_dates = [parse_iso_date(row[3]) for row in datedata]
    if fast_run:
        this_year = datetime.date.today().year
        all_years = [this_year, this_year - 1]
    else:
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
                    filename = get_session_filename_from_date(day_date)
                    if filename and filename.endswith('json'):
                        # sacar a topword
                        s = json.load(open(filename, 'r'))
                        if 'stats' in s:
                            topword = s['stats']['topwords']['session'][0][0]
                            datedict[year][month][day_number]['topword'] = topword
    return datedict


def get_session_from_legsessnum(leg, sess, num):
    # encontrar .txt ou .json
    filename = get_session_filename_from_number(leg, sess, num)
    if not filename:
        return None
    text = codecs.open(filename, 'r', 'utf-8').read()
    if filename.endswith('.json'):
        return json.loads(text)
    elif filename.endswith('.txt'):
        entries = text.split('\n\n')
        newentries = []
        for e in entries:
            # adicionar linebreak extra para dividir parágrafos
            newentries.append(e.replace('\n', '\n\n'))
        newtext = "\n\n".join(newentries)
        newhtml = markdown.render(newtext)
        return newhtml.replace("_", "")
    else:
        return text


def get_session_info(leg, sess, num):
    filename = get_session_filename_from_number(leg, sess, num)
    if not filename or filename.endswith('txt'):
        return None
    text = codecs.open(filename, 'r', 'utf-8')
    data = json.load(text)
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


if __name__ == '__main__':
    result = get_session_filename_from_number(11, 1, 19)
    assert result.split('/')[-1] == '11-1-019_2010-01-07.json'
    result = get_session_filename_from_date(datetime.date(year=2010, month=1, day=7))
    assert result.split('/')[-1] == '11-1-019_2010-01-07.json'
    result = get_session_filename_from_number(9, 1, 105)
    assert result.split('/')[-1] == '09-1-105.txt'
    result = get_session_filename_from_date(datetime.date(year=2003, month=3, day=27))
    assert result.split('/')[-1] == '09-1-105.txt'
