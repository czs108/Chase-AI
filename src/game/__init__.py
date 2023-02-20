import logging
import sys
from pathlib import Path

from config import Config


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

try:
    cfg = Config()
    cfg.load(Path(__file__).parent.parent.joinpath("config.json"))
except BaseException as err:
    logger.exception(err)
    sys.exit(1)
