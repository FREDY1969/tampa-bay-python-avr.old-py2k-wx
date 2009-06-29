#!/usr/bin/env python

# load_table.py [-i] db csv_file...

from __future__ import with_statement
import sys
import os.path
import contextlib
import sqlite3 as db

Ignore_metainfo = False

def get_backup_version(db_file):
    with open(os.path.join(os.path.split(db_file)[0], 'version')) as f:
        return int(f.readline().strip())

def get_max_version(db_cur):
    db_cur.execute("""select max(version) from db_table""")
    return db_cur.fetchone()[0]

def run():
    global Ignore_metainfo, Backup_version, New_version
    if len(sys.argv) < 3 or sys.argv[1] == '-i' and len(sys.argv) < 4:
        sys.stderr.write("usage: load_table.py [-i] db csv_file...\n")
        sys.exit(2)
    if sys.argv[1] == '-i':
        Ignore_metainfo = True
        db_file = sys.argv[2]
        csv_files = sys.argv[3:]
    else:
        db_file = sys.argv[1]
        csv_files = sys.argv[2:]

    with contextlib.closing(db.connect(db_file)) as db_conn:
        with contextlib.closing(db_conn.cursor()) as db_cur: 
            if not Ignore_metainfo:
                Backup_version = get_backup_version(db_file)
                New_version = get_max_version(db_cur)
            try:
                for csv_file in csv_files:
                    load_file(csv_file, db_cur)
            except Exception:
                db_conn.rollback()
                raise
            db_conn.commit()

def load_file(csv_file, db_cur):
    with open(csv_file) as f:
        old_table_name = os.path.split(csv_file)[1][:-4]
        old_col_names = f.readline().split('\t')
        defaults = {}       # new_col_name: code
        if Ignore_metainfo:
            new_table_name = old_table_name
            new_col_names = old_col_names[:]
            col_name_map = dict(zip(old_col_names, old_col_names)) # old: new
        else:
            db_cur.execute("""select id from db_table
                               where name = ? and version = ?
                           """, (old_table_name, Backup_version))
            table_id = db_cur.fetchone()[0]
            db_cur.execute("""select name from db_table
                               where id = ? and version = ?
                           """, (table_id, New_version))
            new_table_name = db_cur.fetchone()[0]

            db_cur.execute("""select id, col_name from db_column
                               where table_id = ? and version = ?
                           """, (table_id, Backup_version))
            old_col_map = dict(db_cur)
            db_cur.execute("""select id, col_name, python_default from db_column
                               where table_id = ? and version = ?
                           """, (table_id, New_version))
            new_col_names = []
            col_name_map = {}   # old: new
            for id, new_name, python_default in db_cur:
                new_col_names.append(new_name)
                if id in old_col_map:
                    old_name = old_col_map[id]
                    col_name_map[old_name] = new_name
                elif python_default:
                    defaults[new_name] = python_default

        for line in f:
            row = dict(zip(old_col_names, line.split('\t')))
            new_row = dict((col_name_map[old_name], row[old_name])
                           for old_name in col_name_map.keys())
            for name, code in defaults:
                default = None
                exec code
                new_row[name] = default
            db_cur.execute("""insert into %s (%s) values (%s)""" % 
                             (new_table_name, ', '.join(new_col_names),
                              ', '.join('?' * len(new_row))),
                           map(lambda name: repr(new_row[name]),
                               new_col_names))


if __name__ == "__main__":
    run()
