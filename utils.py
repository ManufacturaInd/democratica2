#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil


def replace_letters(s, letters, l):
    for letter in letters:
        s = s.replace(letter, l)
    return s


def slugify(s):
    s = s.strip()
    s = s.lower()
    s = s.replace("-", "")
    s = s.replace(" ", "-")
    s = s.replace("'", "-")
    s = replace_letters(s, u"áàâã", u"a")
    s = replace_letters(s, u"éèê", u"e")
    s = replace_letters(s, u"íì", u"i")
    s = replace_letters(s, u"óòôõ", u"o")
    s = replace_letters(s, u"úù", u"u")
    s = replace_letters(s, u"ç", u"c")
    return s


def to_list(s):
    l = s.split(';')
    new_l = []
    for item in l:
        item = item.strip(' "')
        if item:
            new_l.append(item)
    return new_l


def delete_and_create_dir(d):
    """Deletes a directory if it exists, and creates a new one with the
    same name."""
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)


def create_dir(d):
    """Deletes a directory if it exists, and creates a new one with the
    same name."""
    import os
    if not os.path.exists(d):
        os.makedirs(d)


def format_date(value, format='medium'):
    from babel.dates import format_date as babel_format_date
    import datetime
    from dateutil import parser as dateparser
    if type(value) not in (datetime.date, datetime.datetime):
        value = dateparser.parse(value)
    return babel_format_date(value, format, locale="pt_PT")
