from pathlib import Path


__prog__ = 'rstudio_manager'
__version__ = '1.1'
__author__ = 'George Young'
__maintainer__ = 'George Young'
__email__ = 'bioinformatics@lms.mrc.ac.uk'
__status__ = 'Development'
__license__ = 'MIT'

SESSION_STORE = Path.home() / '.rstudio_manager'
SESSION_STORE.mkdir(exist_ok=True)

SINGULARITY_IMAGE = Path('/opt/resources/apps/rstudio/rstudio_4.2.3.sif')
