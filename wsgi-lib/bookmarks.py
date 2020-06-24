#!/usr/bin/env python3

# system libraries
import os
import time
import string
import re

# local libraries here
import db
from logit import logit


def get_bookmarks():
    retval = []
    dlmatch = re.compile('<dl>', flags=re.I)
    has_matched =  False
    the_file = open('/home/ctucker/public_html/bookmarks.html', 'rb');
    for nextline in the_file:
        textline = nextline.decode('utf-8', 'ignore')
        if dlmatch.search(textline):
            has_matched = True
        if has_matched:
            retval.append(textline.strip())
    return '\n'.join(retval)


if __name__ == '__main__':
    the_bookmarks = get_bookmarks()
    for the_line in the_bookmarks.split('\n'):
        the_printable = the_line.encode('utf-8')
        print(the_printable)
