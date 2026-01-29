import logging

from .constant import *
from .helper import *

logger = logging.getLogger(constant.CORE_LOGGER_NAME)
logging.basicConfig(level=logging.NOTSET)
logger.debug("Core module initialized.")

