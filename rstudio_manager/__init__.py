from pathlib import Path
from string import Template


__prog__ = 'rstudio_manager'
__version__ = '3.0'
__author__ = 'George Young'
__maintainer__ = 'George Young'
__email__ = 'bioinformatics@lms.mrc.ac.uk'
__status__ = 'Production'
__license__ = 'MIT'

SESSION_STORE = Path.home() / '.rstudio_manager'
SESSION_STORE.mkdir(exist_ok=True)

SINGULARITY_STORE = Path('/opt/software/apps/singularity/rstudio')
SINGULARITY_IMAGE = Template(str(SINGULARITY_STORE / 'rstudio_$vers.sif'))

R_VERSIONS = \
    sorted(
        sif.stem.removeprefix('rstudio_')
        for sif in SINGULARITY_STORE.glob('*.sif')
    )
