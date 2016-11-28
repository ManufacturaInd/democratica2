#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
import click
import jinja2
from zenlog import log
from dateutil import parser as dateparser

from utils import create_dir, format_date
from utils_dataset import get_gov_dataset, get_date_dataset, get_govpost_dataset, generate_datedict, generate_mp_list, get_session_contents, get_session_info

OUTPUT_DIR = "dist"
TRANSCRIPTS_PATH = "sessoes/"
MPS_PATH = "deputados/"
PHOTO_URL_BASE = '/assets/img/deputados/'
TEMPLATE_DIR = "templates/"

MESES = ['janeiro', 'fevereiro', u'março', 'abril', 'maio', 'junho', 'julho',
         'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']


def render_template_into_file(env, templatename, filename, context=None, place_in_outdir=True):
    target_dir = os.path.join(OUTPUT_DIR, os.path.dirname(filename))
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    template = env.get_template(templatename)
    if not context:
        context = {}
    html = template.render(**context)
    if place_in_outdir:
        filename = os.path.join(OUTPUT_DIR, filename)
    outfile = codecs.open(filename, 'w', 'utf-8')
    outfile.write(html)
    outfile.close()


@click.option("-f", "--fast-run", help="Generate only a few transcripts to save time", is_flag=True, default=False)
@click.command()
def generate_site(fast_run):
    # Create output dirs
    create_dir(OUTPUT_DIR)
    create_dir(os.path.join(OUTPUT_DIR, TRANSCRIPTS_PATH))
    create_dir(os.path.join(OUTPUT_DIR, MPS_PATH))

    # Init Jinja
    env = jinja2.Environment(loader=jinja2.FileSystemLoader([TEMPLATE_DIR]),
                             extensions=['jinja2htmlcompress.SelectiveHTMLCompress'],
                             trim_blocks=True, lstrip_blocks=True)
    env.filters['date'] = format_date

    # Generate the site!
    log.info("Generating index...")
    render_template_into_file(env, 'index.html', 'index.html')

    log.info("Generating MP index...")
    mps = generate_mp_list()
    context = {"mps": mps}
    render_template_into_file(env, 'mp_list.html', "deputados/index.html", context)

    gov_data = get_gov_dataset()
    govpost_data = list(get_govpost_dataset())
    gov_mp_ids = [int(row[2]) for row in govpost_data if row[2]]
    date_data = get_date_dataset()

    log.info("Generating MP pages...")
    for mp in mps:
        id = int(mp['id'])
        mp['photo_url'] = PHOTO_URL_BASE + str(id) + ".jpg"
        # determine government posts
        if id in gov_mp_ids:
            mp['govposts'] = []
            govpost_rows = [row for row in govpost_data if row[2].strip() and int(row[2]) == id]
            for row in govpost_rows:
                gov_number = int(row[0])
                gov = None
                for r in gov_data:
                    if int(r[1]) == gov_number:
                        gov = {'number': r[1], 'start_date': dateparser.parse(r[2]), 'end_date': dateparser.parse(r[3])}
                        break
                if not gov:
                    print(row)
                    log.critical("Gov not found!")
                mp['govposts'].append({
                    'post': row[3],
                    'start_date': dateparser.parse(row[4]),
                    'end_date': dateparser.parse(row[5]),
                    'gov': gov,
                })
        # Parse dates
        for m in mp['mandates']:
            m['start_date'] = dateparser.parse(m['start_date'])
            m['end_date'] = dateparser.parse(m['end_date'])
            # nice effect: if no end date, set to today

        context = {'mp': mp, 'l': None}
        filename = os.path.join(MPS_PATH, mp['slug'], 'index.html')
        render_template_into_file(env, 'mp_detail.html', filename, context)

    log.info("Generating session index...")
    datedict = generate_datedict()
    all_years = [y for y in datedict]
    for year_number in datedict:
        year = datedict[year_number]
        context = {'year': year,
                   'year_number': year_number,
                   'all_years': all_years,
                   'datedict': datedict,
                   }
        target_dir = os.path.join(TRANSCRIPTS_PATH + "%s/" % year_number)
        filename = target_dir + "index.html"
        render_template_into_file(env, 'day_list.html', filename, context)

    # Get most recent year and make the session index
    y = all_years[-1]
    year = datedict[y]
    context = {'year': year,
               'year_number': year_number,
               'all_years': all_years,
               'datedict': datedict,
               }
    render_template_into_file(env, 'day_list.html', TRANSCRIPTS_PATH + 'index.html', context)

    log.info("Generating HTML session pages...")
    if fast_run:
        COUNTER = 0
    date_data.reverse()
    for leg, sess, num, d, dpub, page_start, page_end in date_data:
        dateobj = dateparser.parse(d)
        contents = get_session_contents(leg, sess, num)
        if not contents:
            log.warn("File for %s-%s-%s is missing from the transcripts dataset!" % (leg, sess, num))
            continue
        info = get_session_info(leg, sess, num)

        target_dir = "%s%d/%02d/%02d" % (TRANSCRIPTS_PATH, dateobj.year, dateobj.month, dateobj.day)
        if not os.path.exists(os.path.join(OUTPUT_DIR, target_dir)):
            create_dir(os.path.join(OUTPUT_DIR, target_dir))
        filename = "%s/index.html" % target_dir
        if type(contents) in (str, unicode):
            context = {'session_date': dateobj,
                       'year_number': year_number,
                       'text': contents,
                       'monthnames': MESES,
                       'pdf_url': 'xpto',
                       }
            if info:
                context['session_info'] = info
            render_template_into_file(env, 'day_detail_plaintext.html', filename, context)
        elif type(contents) == dict:
            contents['session_date'] = dateparser.parse(contents['session_date'])
            contents['monthnames'] = MESES
            # usar entradas do .json como contexto
            render_template_into_file(env, 'day_detail.html', filename, contents)

        if fast_run:
            COUNTER += 1
            if COUNTER > 20:
                break


if __name__ == "__main__":
    generate_site()
