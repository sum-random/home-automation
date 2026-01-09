#!/usr/bin/env python3

# system libraries
import os
import time
import string
import re

# local libraries here
import db
from logit import logit
from config import config


def get_bookmarks():
    retval = []
    dlmatch = re.compile('<dl>', flags=re.I)
    has_matched =  False
    bookmarks = open(config()['path']['bookmarks'], 'rb');
    for nextline in bookmarks:
        textline = nextline.decode('utf-8', 'ignore')
        if dlmatch.search(textline):
            has_matched = True
        if has_matched:
            retval.append(textline.strip())
    return '\n'.join(retval)


if __name__ == '__main__':
    bookmarks = get_bookmarks()
    for line in bookmarks.split('\n'):
        printable = line.encode('utf-8')
        print(printable)
