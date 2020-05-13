from pathlib import Path
from logging.handlers import RotatingFileHandler

from cb_bdti.config import constants as const


class DirFileHandler(RotatingFileHandler):
	"""
	Logging handler to create a directory for the logs of the application. Then it generates log files as it was
	configured, following ``RotatingFileHandler`` behaviour.
	"""

	def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
		Path(const.LOG_FOLDER_PATH).mkdir(exist_ok=True)
		log_path = const.LOG_FOLDER_PATH / filename
		RotatingFileHandler.__init__(self, log_path, mode, maxBytes, backupCount, encoding, delay)
