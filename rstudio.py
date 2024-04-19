#!/usr/bin/python3.9

''' rstudio: launch and manage rstudio servers as HPC jobs '''

###############################################################################
#   ____  ____  ____  _  _  ____  __  __
#  (  _ \/ ___)(_  _)/ )( \(    \(  )/  \
#   )   /\___ \  )(  ) \/ ( ) D ( )((  O )
#  (__\_)(____/ (__) \____/(____/(__)\__/
#
###############################################################################


import argparse
from random import choices
from string import hexdigits
import sys

from rich import print
from rich_argparse import RawDescriptionRichHelpFormatter

from rstudio_manager import __prog__, __version__, __status__, SESSION_STORE
from rstudio_manager.commands import rstudio_start, rstudio_stop, rstudio_list


# argparse ####################################################################


commands = {}

parser = argparse.ArgumentParser(
    prog='rstudio',
    description=r'''
                   ____  ____  ____  _  _  ____  __  __
                  (  _ \/ ___)(_  _)/ )( \(    \(  )/  \
                   )   /\___ \  )(  ) \/ ( ) D ( )((  O )
                  (__\_)(____/ (__) \____/(____/(__)\__/

               launch and manage RStudio servers as HPC jobs
''',
    formatter_class=RawDescriptionRichHelpFormatter,
    exit_on_error=False,
    allow_abbrev=False)
subparsers = parser.add_subparsers(
    title='commands',
    metavar='{command}',
    dest='command',
    required=True)

parser.add_argument(
    '-v', '--version',
    action='version', version=f'{__prog__} v{__version__} ({__status__})',
    help='show the program version and exit')
parser.add_argument(
    '-q', '--quiet', action='store_true',
    help='silence logging information')

#
# rstudio start
#

commands['start'] = subparsers.add_parser(
    'start',
    aliases=['create', 'new'],
    help='start a new RStudio server',
    description='start a new RStudio server',
    formatter_class=RawDescriptionRichHelpFormatter)
# register the alias names as placeholders
commands['create'] = commands['new'] = commands['start']
# arguments
commands['start'].add_argument(
    'conda', type=str,
    help='name of an existing conda environment containing R')
commands['start'].add_argument(
    '-n', '--name', default='rstudio_server', type=str,
    help='job name for the scheduler (default "%(default)s")')
commands['start'].add_argument(
    '-@', '--cpu', default=1, type=int,
    help='requested number of CPUs (default %(default)s)')
commands['start'].add_argument(
    '-m', '--mem', default=8, type=int,
    help='requested amount of RAM (GB, default %(default)s)')
commands['start'].add_argument(
    '-w', '--wallclock', dest='time', default=16, type=int,
    help='requested runtime (hrs, default %(default)s)')
commands['start'].add_argument(
    '-g', '--gpu', default=0, type=int,
    help='requested number of GPUs (default %(default)s)')
commands['start'].add_argument(  # hidden
    '-p', '--partition', default='int', type=str,
    help=argparse.SUPPRESS)
commands['start'].add_argument(
    '-t', '--token', type=str, default=''.join(choices(hexdigits, k=8)),
    help='password token for the session (auto-generated by default)')
commands['start'].add_argument(
    '-b', '--bind', type=str, default='',
    help='additional bind path/s using the singularity format \
    specification (src[:dest[:opts]])')
commands['start'].add_argument(  # hidden
    '-l', '--log', action='store_true',
    help=argparse.SUPPRESS)

#
# rstudio stop
#

commands['stop'] = subparsers.add_parser(
    'stop',
    aliases=['delete', 'cancel', 'kill'],
    help='stop an existing RStudio server instance',
    description='stop an existing RStudio server instance',
    formatter_class=RawDescriptionRichHelpFormatter)
# register the alias names as placeholders
commands['delete'] = commands['cancel'] = commands['kill'] = commands['stop']
# arguments
commands_stop.add_argument(
    'job', type=str, nargs='*',
    help='list of job number/s and/or name/s to kill')
commands_stop.add_argument(
    '-a', '--all', action='store_true',
    help='stop all running RStudio instances')

#
# rstudio list
#

commands['list'] = subparsers.add_parser(
    'list',
    aliases=['ls'],
    help='list running RStudio servers',
    description='list running RStudio servers',
    formatter_class=RawDescriptionRichHelpFormatter)
# register the alias names as placeholders
commands['ls'] = commands['list']


# main ########################################################################


def main():

    # catch program name by itself
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    # catch command names by themselves
    if len(sys.argv) == 2 and \
            (sys.argv[1] in commands and
            sys.argv[1] not in ('list', 'ls')):
        commands[sys.argv[1]].print_help()
        sys.exit(0)

    # catch unknown commands and errors
    try:
        args = parser.parse_args()
    except argparse.ArgumentError:
        parser.print_help()
        sys.exit(1)

    # Run the relevant command from rstudio_manager.commands
    if args.command in ('start', 'create'):
        rstudio_start(args)
    elif args.command in ('stop', 'delete', 'cancel', 'kill'):
        rstudio_stop(args)
    elif args.command in ('list', 'ls'):
        rstudio_list(args)


if __name__ == '__main__':
    main()