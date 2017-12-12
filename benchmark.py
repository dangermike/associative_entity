#!/usr/bin/env python

import MySQLdb
import psycopg2
import statistics

from datetime import datetime
from itertools import islice
from random import randint


def read_lines(file_path):
    with open(file_path, 'r') as f:
        line = f.readline().rstrip()
        while line:
            yield line
            line = f.readline().rstrip()


def random_item(source):
    max_ix = len(source) - 1

    while True:
        yield source[randint(0, max_ix)]


C2P_SNTH = """
SELECT
  p.name
FROM
  assoc_test.people p JOIN
  assoc_test.people_companies_id pc
    ON p.id = pc.p_id JOIN
  assoc_test.companies c
    ON c.id = pc.c_id
WHERE
  c.name in (%s)"""

C2P_COMP = """
SELECT
  p.name
FROM
  assoc_test.people p JOIN
  assoc_test.people_companies_id pc
    ON p.id = pc.p_id JOIN
  assoc_test.companies c
    ON c.id = pc.c_id
WHERE
  c.name in (%s)"""

P2C_SNTH = """
SELECT
  c.name
FROM
  assoc_test.people p JOIN
  assoc_test.people_companies_id pc
    ON p.id = pc.p_id JOIN
  assoc_test.companies c
    ON c.id = pc.c_id
WHERE
  p.name in (%s)"""

P2C_COMP = """
SELECT
  c.name
FROM
  assoc_test.people p JOIN
  assoc_test.people_companies_id pc
    ON p.id = pc.p_id JOIN
  assoc_test.companies c
    ON c.id = pc.c_id
WHERE
  p.name in (%s)"""


def db_exec(conn, query):
    c=conn.cursor()
    c.execute(q)
    ret = c.fetchall()
    c.close()
    return ret



people = list(map(lambda x: x.split(',')[1], read_lines('trg_lists/people.txt')))
companies = list(map(lambda x: x.split(',')[1], read_lines('trg_lists/companies.txt')))

reps = 100
ipq = 1000

for db in [
    MySQLdb.connect("localhost","root","","assoc_test"),
    psycopg2.connect(database='dangermike'),
]:
    ctype = db.__class__.__module__.split('.')[0]
    try:
        for name, q_template, data in [
            ('C2P_SNTH', C2P_SNTH, random_item(companies)),
            ('C2P_COMP', C2P_COMP, random_item(companies)),
            ('P2C_SNTH', P2C_SNTH, random_item(people)),
            ('P2C_COMP', P2C_COMP, random_item(people)),
        ]:
            times = [0.0] * reps

            for ix in range(reps):
                q = q_template % ','.join(["'%s'" % x for x in islice(data, ipq)])

                start = datetime.utcnow()
                db_exec(db, 1)
                dur = datetime.utcnow() - start
                times[ix] = dur.total_seconds()
            print(
                '%s %s: %d reps of %d items per query completed in %f secs (%f average, %f median, %f stdev)' %
                (ctype, name, reps, ipq, sum(times), statistics.mean(times), statistics.median(times), statistics.stdev(times))
            )
    finally:
        db.close()
