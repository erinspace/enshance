import logging
logger = logging.getLogger(__name__)

from .defaults import *

try:
    from .local import *
except ImportError as error:
    logger.warn("No enshance local.py settings file found. Try running $ cp enshance/enshance/settings/local-dist.py enshance/enshance/settings/local.py. Defaulting to enshance/settings/local.py")
    from enshance.settings.local import *
