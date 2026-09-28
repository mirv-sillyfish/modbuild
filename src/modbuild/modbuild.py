#!/usr/bin/env python3

import argparse
import hashlib
from pathlib import Path
import runpy

import db

def main():
    """ Main entry point to modbuild. """
    cwd = Path.cwd()
    modfile = 'build.py'

    buildfile = cwd / modfile
    if not buildfile.exists():
        print('Could not find build.py file')
        exit(1)

    db.db_open(cwd / 'modbuild.sqlite')
    # Take an md5 of the build file and compare it against any existing
    # database entry. If the entry doesn't exist or doesn't match, drop
    # (clean) the whole db to force an entire rebuild of the project.
    with open(buildfile, 'rb') as sfile:
        data = sfile.read()
        md5 = hashlib.md5(data).hexdigest()
        key = str(buildfile)
        if md5 != db.db_query_md5(key):
            db.db_clean()
            db.db_insert_md5(key, md5)

    runpy.run_path(buildfile)

    # Done, close off the database connection.
    db.db_close()


if __name__ == '__main__':
    main()
