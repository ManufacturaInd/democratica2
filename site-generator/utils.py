#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil


def replace_letters(s, letters, l):
    '''Replace all specified characters with a substring.'''
    for letter in letters:
        s = s.replace(letter, l)
    return s


def slugify(s):
    '''Creates accent-aware slugs based on human formatted strings.'''
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
    '''Convert a ;-separated string into a list.'''
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
    """Creates a new directory unless it exists."""
    import os
    if not os.path.exists(d):
        os.makedirs(d)


def format_date(value, format='medium'):
    """Parse a date object or string using dateutil and return a pt_PT
    localized string using babel."""
    from babel.dates import format_date as babel_format_date
    import datetime
    if not value:
        return None
    from dateutil import parser as dateparser
    if type(value) not in (datetime.date, datetime.datetime):
        value = dateparser.parse(value)
    return babel_format_date(value, format, locale="pt_PT")


def quick_hash_file(filename):
    import sys
    import hashlib
    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536
    md5 = hashlib.md5()
    with open(sys.argv[1], 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()
