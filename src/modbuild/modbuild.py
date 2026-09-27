import argparse
from pathlib import Path
import runpy

from db import db_open, db_close
#import db

def main():
    """ Main entry point to modbuild. """
    cwd = Path.cwd()

    parser = argparse.ArgumentParser(
        prog='modbuild',
        description='Builder for C++ module based application.',
        epilog="If you need help, please don't. Hesitate to ask.")
    parser.add_argument('--clean', help='clean build directory of generated files', action='store_true')
    parser.add_argument('--file', help='specify which file to use for building')
    args = parser.parse_args()

    modfile = 'build.py'

    buildfile = cwd / modfile
    if not buildfile.exists():
        print('Could not find modbuild.py file')
        exit(1)

    # TODO: take an md5 of the modbuild.py file and compare it against any existing
    #       database entry. If the entry doesn't exist or doesn't match, drop the
    #       whole thing. This will force an entire rebuild of the project.
    db_open(cwd / 'scoms.sqlite')
    runpy.run_path(buildfile)
    db_close()


if __name__ == '__main__':
    main()
