import logging

from .constant import *
from .helper import *

logging.basicConfig(level=logging.INFO)

# Silence noisy third-party loggers
logging.getLogger("websockets").setLevel(logging.WARNING)
logging.getLogger("websockets.client").setLevel(logging.WARNING)
logging.getLogger("nodriver").setLevel(logging.WARNING)
logging.getLogger("nodriver.core.connection").setLevel(logging.WARNING)
logging.getLogger("nodriver.core.browser").setLevel(logging.WARNING)

logger = logging.getLogger(constant.CORE_LOGGER_NAME)
logger.debug("Core module initialized.")

