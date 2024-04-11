from pathlib import Path, PurePath
import sys


__prog__ = 'rstudio_manager'
__version__ = '0.1'
__author__ = 'George Young'
__maintainer__ = 'George Young'
__email__ = 'bioinformatics@lms.mrc.ac.uk'
__status__ = 'Development'
__license__ = 'MIT'

SESSION_STORE = Path.home() / '.rstudio_manager'
SIF_STORE = Path('/opt/resources/apps/rstudio')

R_VERSIONS = \
    sorted(
        str(PurePath(sif).stem).removeprefix('rstudio_')
        for sif in SIF_STORE.glob('*.sif')
    )
if not R_VERSIONS:
    print(f'No singularity images could be found within: {SIF_STORE}')
    sys.exit(1)