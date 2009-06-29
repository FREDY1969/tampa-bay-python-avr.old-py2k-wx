#!/usr/bin/env python

# create_tables.py db

from __future__ import with_statement
import sys
import os.path
import contextlib
import sqlite3 as db

def get_backup_version(db_file):
    with open(os.path.join(os.path.split(db_file)[0], 'version')) as f:
        return int(f.readline().strip())

def get_max_version(db_cur):
    db_cur.execute("""select max(version) from db_table""")
    return db_cur.fetchone()[0]

def run():
    global Backup_version, New_version

    if len(sys.argv) != 2:
        sys.stderr.write("usage: create_tables.py db\n")
        sys.exit(2)

    db_file = sys.argv[1]

    with contextlib.closing(db.connect(db_file)) as db_conn:
        with contextlib.closing(db_conn.cursor()) as db_cur: 
            Backup_version = get_backup_version(db_file)
            New_version = get_max_version(db_cur)
            db_cur.execute("""select new_table.id, new_table.table_name
                                from db_table as new_table
                               where new_table.version = ?
                                 and not exists(select id from db_table
                                                where id = new_table.id
                                                  and version = ?)
                           """, (New_version, Backup_version))
            try:
                for id, table_name in db_cur.fetchall():
                    create_table(id, table_name, db_cur)
            except Exception:
                db_conn.rollback()
                raise
            db_conn.commit()

def create_table(id, table_name, db_cur):
    db_cur.execute("""select col_name, definition from db_column
                       where table_id = ? and version = ?
                       order by position
                   """, (id, New_version))
    for name, defn in db_cur:
        if name is not None:
            lines.append("    %s %s" % (name, defn))
        else:
            lines.append("    %s" % (defn,))
    command += ");"
    db_cur.execute("create table %s (\n%s\n)" % (table_name, ',\n'.join(lines)))


if __name__ == "__main__":
    run()
