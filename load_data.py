#!/usr/bin/env python

import _mysql
import itertools
import collections


def read_lines(file_path):
    with open(file_path, 'r') as f:
        line = f.readline().rstrip()
        while line:
            yield line
            line = f.readline().rstrip()


DbItem = collections.namedtuple('DbItem', 'name, columns, formatter')

items = [
    DbItem(
        'people',
        ['id', 'name'],
        lambda x: "({},'{}')".format(*x.split(','))),
    DbItem(
        'companies',
        ['id', 'name'],
        lambda x: "({},'{}')".format(*x.split(','))),
    DbItem(
        'people_companies',
        ['p_id', 'c_id'],
        lambda x: "({},{})".format(*x.split(','))),
    DbItem(
        'people_companies_id',
        ['id', 'p_id', 'c_id'],
        lambda x: "({},{},{})".format(*x.split(','))),
]



db = _mysql.connect("localhost","root","","assoc_test")
try:
    for item in reversed(items):
        db.query('DELETE FROM %s' % item.name)

    for item in items:
        q = "INSERT INTO %s (%s) VALUES " % (item.name, ','.join(item.columns))

        last_len = -1
        lines = read_lines('trg_lists/%s.txt' % item.name)

        while last_len != 0:
            vals = ','.join(map(item.formatter, itertools.islice(lines, 1000)))
            last_len = len(vals)
            if last_len > 0:
                qx = q + vals
                db.query(qx)
finally:
    db.close()
