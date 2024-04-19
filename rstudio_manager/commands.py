from argparse import Namespace
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from time import sleep

from rich.console import Console
from rich.table import Table
import sh

from rstudio_manager import SINGULARITY_IMAGE, SESSION_STORE
from rstudio_manager.helpers import \
    get_logger, get_rstudio_jobs, cancel_job, Request, Session, SignalHandler


# globals #####################################################################


sbatch = sh.Command('/opt/slurm/22.05.8/bin/sbatch')


# functions ###################################################################


def rstudio_start(args: Namespace) -> None:
    '''
    Start a new rstudio server

    Parameters:
        args (argparse.Namespace): a parsed program call from `parse_args()`
    '''

    logger = get_logger('rstudio_start', args.quiet)

    # validate the request against the partition limits
    logger.info('Validating the request')
    request = Request(args.partition, args.cpu, args.mem, args.gpu, args.time)

    with NamedTemporaryFile(
                mode='r', prefix='rstudio_', suffix='.log', dir=SESSION_STORE,
                delete=not args.log
            ) as tmpfile:
        try:
            # submit the job
            logger.info('Submitting the job')
            exports = {
                'PASSWORD': args.token,
                'RSTUDIO_SIF': str(SINGULARITY_IMAGE),
                'BIND_PATHS': f'"{args.bind}"',
                "CONDA_ENV": f'{args.conda}'
            }
            job_id = \
                sbatch(
                    *request.format(args.name, tmpfile),
                    '--export', ','.join((f'{k}={v}' for k, v in exports.items())),
                    str(Path(__file__).resolve().parent / "job_template.sh")
                ).strip()
            session = Session(job_id, args.quiet)
            session.write()
        except sh.ErrorReturnCode:
            print(job_id)
            logger.error('`sbatch` had a non-zero exit status')  # exit(1)
        # wait for the job to schedule
        logger.info(f'Waiting for job {job_id} to schedule')
        session.wait()
        if not session.is_running:
            logger.error('Job failed to schedule correctly')
        # wait for rstudio to launch
        logger.info("Waiting for RStudio to launch")
        # skip to the end of the file to test for script output
        with SignalHandler(cancel_job, job_id):
            tmpfile.seek(0, 2)
            while tmpfile.tell() == 0:
                sleep(2)
                tmpfile.seek(0, 2)
            tmpfile.seek(0)
            session.url = f'http://{tmpfile.readline().strip()}'
            session.token = args.token
            session.write()
            # wait until we can connect to the session
            while not session.is_alive:
                sleep(2)
        logger.info(f'\nRStudio is running')
        # print so that those using -q see the output
        print(f'URL:   {session.url}')
        print(f'Token: {session.token}')


def rstudio_stop(args: Namespace) -> None:
    '''
    Stop an existing rstudio server instance

    Parameters:
        args (argparse.Namespace): a parsed program call from `parse_args()`
    '''

    for session in get_rstudio_jobs():
        if args.all or \
                (args.job and
                    (session.job_id in args.job) or
                    (session.job_name in args.job)):
            cancel_job(session.job_id)


def rstudio_list(args: Namespace) -> None:
    '''
    Rich print running rstudio servers

    Parameters:
        args (argparse.Namespace): a parsed program call from `parse_args()`
    '''

    sessions = tuple(get_rstudio_jobs())
    if not sessions:
        print('No RStudio servers are running')
        sys.exit(0)

    table = Table(title="Active RStudio Servers")
    table.add_column("Job ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Name", justify="left")
    table.add_column("URL", justify="left", no_wrap=True)
    table.add_column("Token", justify="left", no_wrap=True)

    for session in get_rstudio_jobs():
        table.add_row(
            session.job_id, session.job_name, session.url, session.token
        )

    console = Console()
    console.print(table)