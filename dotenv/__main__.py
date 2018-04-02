import argparse
import logging
from subprocess import PIPE, STDOUT
import subprocess
import os
import sys

from dotenv import dotenv_values


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


parser = argparse.ArgumentParser()
parser.add_argument('command', type=str, nargs=argparse.REMAINDER)
args = parser.parse_args()


def main():
    global args
    command = args.command
    logger.debug(command)

    de_dict = dotenv_values()
    logger.debug(de_dict)

    if not command:
        logger.warning('No command given, doing nothing.')
        return

    os.environ.update(de_dict)

    p = subprocess.Popen(command,
                         stdin=PIPE,
                         stdout=PIPE,
                         stderr=STDOUT,
                         universal_newlines=True,
                         bufsize=0,
                         shell=False)
    try:
        out, _ = p.communicate()
        print(out)
    except Exception:
        logger.error('Oops!')
        out, _ = p.communicate()
        logger.error(out)

    sys.exit(p.returncode)


if __name__ == '__main__':
    main()
