from pathlib import Path
from string import Template


__prog__ = 'rstudio_manager'
__version__ = '2.0'
__author__ = 'George Young'
__maintainer__ = 'George Young'
__email__ = 'bioinformatics@lms.mrc.ac.uk'
__status__ = 'Production'
__license__ = 'MIT'

SESSION_STORE = Path.home() / '.rstudio_manager'
SESSION_STORE.mkdir(exist_ok=True)

SINGULARITY_IMAGE = Template('/opt/resources/apps/rstudio/lmsbio/rstudio_$vers.sif')

R_VERSIONS = (
    '4.4.0',
)
