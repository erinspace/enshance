import logging
logger = logging.getLogger(__name__)

from .defaults import *

try:
    from .local import *
except ImportError as error:
    logger.warn("No enshance local.py settings file found. Try running $ cp enshance/enshance/settings/local-dist.py enshance/enshance/settings/local.py. Defaulting to enshance/settings/local.py")
    from enshance.settings.local import *


CELERY_ENABLE_UTC = True
CELERY_RESULT_BACKEND = None
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_ACCEPT_CONTENT = ['pickle']
CELERY_RESULT_SERIALIZER = 'pickle'
CELERY_IMPORTS = ('enshance.tasks')
