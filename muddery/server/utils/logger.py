"""
Logging facilities

These are thin wrappers on logging facilities; logs
are all directed either to stdout or to $GAME_DIR/server/logs.

"""

from muddery.common.utils.logger import Logger
from muddery.server.settings import SETTINGS


logger = Logger(SETTINGS.LOG_NAME, SETTINGS.LOG_FILE, SETTINGS.LOG_LEVEL, SETTINGS.LOG_TO_CONSOLE)
