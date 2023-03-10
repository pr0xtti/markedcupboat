# Logging
import logging
# For environment settings
import os
from pathlib import Path
from dotenv import load_dotenv
# For mongodb connection string
from urllib.parse import quote_plus

# For settings from config.yaml
import confuse

# Application name
APP_NAME = "markedcupboat"
# Logging configuration file
CONFIG_FILE = 'logging_config.yaml'
# Logging level
DEFAULT_LEVEL = logging.WARNING

logger = logging.getLogger(f"{APP_NAME}.{__name__}")


class Settings:
    # Variables that defined by Task
    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGO_DB_ADDRESS: str
    TW_ACCESS_TOKEN: str
    TW_ACCESS_TOKEN_SECRET: str
    TW_CONSUMER_KEY: str
    TW_CONSUMER_KEY_SECRET: str
    __ATTRS = [
        "MONGODB_USER",
        "MONGODB_PASSWORD",
        "MONGO_DB_ADDRESS",
        "TW_ACCESS_TOKEN",
        "TW_ACCESS_TOKEN_SECRET",
        "TW_CONSUMER_KEY",
        "TW_CONSUMER_KEY_SECRET",
    ]
    # Local configuration file name
    CONFIG_FILE: str = 'config.yaml'

    # Make a connection string
    def make_connection_string(self) -> str:
        return (
            f"mongodb+srv://{quote_plus(self.MONGODB_USER)}:"
            f"{quote_plus(self.MONGODB_PASSWORD)}@"
            f"{self.MONGO_DB_ADDRESS}"
        )

    @staticmethod
    def check_not_less_zero(variable, default):
        if not variable:
            return default
        try:
            if int(variable) < 0:
                return 0
        except:
            return default

    def __init__(self):
        # Check if environment variables exist
        try:
            # Setting parameters for mongodb
            logger.debug(f"Trying to getenv from environment")
            for attr in self.__ATTRS:
                attr_value = os.getenv(attr)
                if attr_value:
                    logger.debug(f"Found env variable: {attr}")
                    setattr(self, attr, attr_value)
                else:
                    logger.debug(f"Couldn't getenv variable: {attr}")
                    raise Exception(f"Couldn't getenv environment")
        except:
            # Not less than one variable doesn't exist in environment
            # Going to get variables from .env
            logger.debug('Environment variables not found. Setting env from .env file')
            env_path = Path(".") / ".env"
            load_dotenv(dotenv_path=env_path, verbose=True)

            for attr in self.__ATTRS:
                attr_value = os.getenv(attr)
                if attr_value:
                    logger.debug(f"Read from file, variable: {attr}")
                    setattr(self, attr, attr_value)
                else:
                    logger.critical(f"Couldn't getenv variable: {attr}")
                    raise Exception(f"Couldn't getenv environment")
        finally:
            # Building connection string for mongodb
            self.MONGODB_URI: str = self.make_connection_string()

        try:
            # Setting other params from local configuration file for the project
            conf = confuse.Configuration(__name__)
            conf.set_file(self.CONFIG_FILE)
            # Database name inside mongodb
            self.MONGODB_DBNAME = conf['mongodb']['dbname'].get()
            if self.MONGODB_DBNAME:
                logger.debug(f"Found: MONGODB_DBNAME: {self.MONGODB_DBNAME}")
            # Mongodb collections names
            self.PAIRS_NAME = conf['mongodb']['pairs'].get()
            self.POSTS_NAME = conf['mongodb']['posts'].get()
            self.TOP_LIMIT = conf['mongodb']['pairs_top_limit'].get()
            self.MESSAGE_TEMPLATE = conf['message']['template'].get()
            self.VENUES_LIMIT = conf['message']['venues_limit'].get()

            # Mongodb timeout serverSelectionTimeoutMS
            self.SERVERSELECTIONTIMEOUTMS: str = \
                conf['mongodb']['serverselectiontimeoutms'].get()
            self.CLIENT_MAXTIMEMS: str = conf['mongodb']['client_maxtimems'].get()

            # Twitter
            self.TWEETS_URL = conf['twitter']['tweets_url'].get()

            # Global app timeout
            self.GLOBAL_TIMEOUT = self.check_not_less_zero(
                conf['global']['global_timeout'].get(),
                default=600
            )
            # Retry count. -1 or 0: infinity
            self.GLOBAL_RETRY = self.check_not_less_zero(
                conf['global']['global_retry'].get(),
                default=3
            )
            # Sleep interval
            self.GLOBAL_INTERVAL = self.check_not_less_zero(
                conf['global']['global_interval'].get(),
                default=5
            )
            # Retry count. -1 or 0: infinity
            self.INNER_RETRY = self.check_not_less_zero(
                conf['global']['inner_retry'].get(),
                default=3
            )
            # Sleep interval
            self.INNER_INTERVAL = self.check_not_less_zero(
                conf['global']['inner_interval'].get(),
                default=5
            )

        except Exception as e:
            logger.critical(
                f"Failed configure from file: {self.CONFIG_FILE}: {e}"
            )


settings = Settings()
