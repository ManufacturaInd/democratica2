#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import codecs
import click
import jinja2
from zenlog import log
from dateutil import parser as dateparser
from collections import OrderedDict
import markdown

from utils import create_dir, format_date, years_since
from utils_dataset import get_gov_dataset, get_date_dataset, get_govpost_dataset, generate_datedict, generate_mp_list, get_session_from_legsessnum, get_session_info

MESES = ['janeiro', 'fevereiro', u'março', 'abril', 'maio', 'junho', 'julho',
         'agosto', 'setembro', 'outubro', 'novembro', 'dezembro']


class SiteGenerator(object):
    def __init__(self, fast_run=False):
        self.output_dir = "dist"
        self.sessions_path = "sessoes/"
        self.mps_path = "deputados/"
        self.photos_base_url = '/assets/img/deputados/'
        self.templates_path = "templates/"
        self.loaded_templates = {}
        self.fast_run = fast_run
        self.fast_run_count = 20

        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader([self.templates_path]),
                                      extensions=[
                                          'jinja2htmlcompress.SelectiveHTMLCompress',
                                          'jinja2.ext.with_'],
                                      trim_blocks=True, lstrip_blocks=True)
        self.env.filters['date'] = format_date
        self.md = markdown.Markdown(extensions=['meta'])

        self.mps = None

        create_dir(self.output_dir)
        create_dir(os.path.join(self.output_dir, self.sessions_path))
        create_dir(os.path.join(self.output_dir, self.mps_path))

    def render_template_into_file(self, templatename, filename, context=None, place_in_outdir=True):
        target_dir = os.path.join(self.output_dir, os.path.dirname(filename))
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        if not self.loaded_templates.get(templatename):
            template = self.env.get_template(templatename)
            self.loaded_templates[templatename] = template
        else:
            # load "cached" template
            template = self.loaded_templates.get(templatename)
        if not context:
            context = {}
        html = template.render(**context)
        if place_in_outdir:
            filename = os.path.join(self.output_dir, filename)
        outfile = codecs.open(filename, 'w', 'utf-8')
        outfile.write(html)
        outfile.close()

    def generate_homepage(self):
        context = {"intro_text": self.md.convert(codecs.open('content/intro.md', 'r', 'utf-8').read())}
        self.render_template_into_file('index.html', 'index.html', context)

    def generate_single_pages(self):
        for pname in ("acerca", "faq", "dados"):
            context = {"md_content": self.md.convert(codecs.open('content/%s.md' % pname, 'r', 'utf-8').read()),
                       "page_name": pname}
            self.render_template_into_file('single-page.html', '%s/index.html' % pname, context)

    def generate_mp_index(self):
        if not self.mps:
            self.mps = generate_mp_list(only_active=False)
        context = {"mps": self.mps,
                   'page_name': 'deputados'}
        self.render_template_into_file('mp_list.html', "deputados/index.html", context)

    def generate_mp_pages(self):
        self.gov_data = get_gov_dataset()
        self.govpost_data = list(get_govpost_dataset())
        self.gov_mp_ids = [int(row[2]) for row in self.govpost_data if row[2]]
        if not self.mps:
            self.mps = generate_mp_list(only_active=False)
        for mp in self.mps:
            id = int(mp['id'])
            mp['photo_url'] = self.photos_base_url + str(id) + ".jpg"
            # determine government posts
            if id in self.gov_mp_ids:
                mp['govposts'] = []
                govpost_rows = [row for row in self.govpost_data if row[2].strip() and int(row[2]) == id]
                for row in govpost_rows:
                    gov_number = int(row[0])
                    gov = None
                    for r in self.gov_data:
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

            context = {'mp': mp,
                       'mp_age': years_since(dateparser.parse(mp['birthdate']).date()) if 'birthdate' in mp else None,
                       'l': None,
                       'page_name': 'deputados'}
            filename = os.path.join(self.mps_path, mp['slug'], 'index.html')
            self.render_template_into_file('mp_detail.html', filename, context)

    def generate_session_index(self):
        self.datedict = generate_datedict(self.fast_run)
        all_years = [y for y in self.datedict]
        for year_number in self.datedict:
            year = self.datedict[year_number]
            context = {'year': year,
                       'year_number': year_number,
                       'all_years': all_years,
                       'datedict': self.datedict,
                       'months': MESES,
                       'months_short': [m[:3] for m in MESES],
                       'page_name': 'sessoes',
                       }
            target_dir = os.path.join(self.sessions_path + "%s/" % year_number)
            filename = target_dir + "index.html"
            self.render_template_into_file('session_list.html', filename, context)
        # Get most recent year and make the session homepage (when you open the "sessions" tab)
        y = all_years[-1]
        year = self.datedict[y]
        context = {'year': year,
                   'year_number': year_number,
                   'all_years': all_years,
                   'datedict': self.datedict,
                   'months': MESES,
                   'months_short': [m[:3] for m in MESES],
                   'page_name': 'sessoes',
                   }
        self.render_template_into_file('session_list.html', self.sessions_path + 'index.html', context)

    def generate_session_pages(self):
        self.date_data = get_date_dataset()
        self.date_data.reverse()
        if self.fast_run:
            COUNTER = 0
        for leg, sess, num, d, dpub, page_start, page_end in self.date_data:
            dateobj = dateparser.parse(d)
            session = get_session_from_legsessnum(leg, sess, num)
            if not session:
                log.warn("File for %s-%s-%s is missing from the transcripts dataset!" % (leg, sess, num))
                continue
            target_dir = "%s%d/%02d/%02d" % (self.sessions_path, dateobj.year, dateobj.month, dateobj.day)
            filename = "%s/index.html" % target_dir
            info = get_session_info(leg, sess, num)
            create_dir(os.path.join(self.output_dir, target_dir))

            if type(session) in (str, unicode):
                # sessão em texto simples
                context = {'date': dateobj,
                           'year_number': dateobj.year,
                           'leg': leg,
                           'sess': sess,
                           'num': num,
                           'text': session,
                           'monthnames': MESES,
                           'pdf_url': 'xpto',
                           'page_name': 'sessoes',
                           }
                if info:
                    context['session_info'] = info
                self.render_template_into_file('session_plaintext.html', filename, context)

            elif type(session) in (dict, OrderedDict):
                # usar entradas do .json como contexto
                session['date'] = dateparser.parse(session['session_date'])
                session['monthnames'] = MESES
                session['page_name'] = 'sessoes'
                self.render_template_into_file('session.html', filename, session)
            if self.fast_run:
                COUNTER += 1
                if COUNTER > self.fast_run_count:
                    break


@click.option("-r", "--render", default="all", help="Render a specific template", show_default=True)
@click.option("-f", "--fast-run", help="Generate only a few transcripts to save time", is_flag=True, default=False)
@click.command()
def generate_site(fast_run, render):
    sg = SiteGenerator(fast_run)

    if render == "homepage":
        sg.generate_homepage()
    elif render == "single_pages":
        sg.generate_single_pages()
    elif render == "mp_index":
        sg.generate_mp_index()
    elif render == "mp_pages":
        sg.generate_mp_pages()
    elif render == "session_index":
        sg.generate_session_index()
    elif render == "session_pages":
        sg.generate_session_pages()
    elif render == "all":
        # log.info("Generating index...")
        sg.generate_homepage()
        sg.generate_single_pages()
        # log.info("Generating MP index...")
        sg.generate_mp_index()
        # log.info("Generating MP pages...")
        sg.generate_mp_pages()
        # log.info("Generating session pages...")
        sg.generate_session_pages()
        # log.info("Generating session index...")
        sg.generate_session_index()
    else:
        raise click.BadParameter("invalid parameter for render option")


if __name__ == "__main__":
    generate_site()
