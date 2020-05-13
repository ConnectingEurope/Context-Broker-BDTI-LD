import yaml

import logging.config
import cb_bdti.utils.loggers.handlers
from cb_bdti.config import constants as const


def config_logging():
    """
    Configures logging library.
    
    It loads the YAML file on the project that establishes the different loggers and their handlers.

    :return: None
    """
    with open(const.BASE_PATH / 'config' / 'logger' / 'logger.yml', 'r') as file:
        config = yaml.safe_load(file.read())
        logging.config.dictConfig(config)
