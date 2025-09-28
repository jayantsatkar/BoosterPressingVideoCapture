import logging
from logging.handlers import TimedRotatingFileHandler
import os

class LogError:
    def __init__(self):
        print('In CTOR of Error Logger')

    @staticmethod
    def GetLogger():
        LOG_FORMAT = '%(levelname)s %(asctime)s -- %(message)s'
        DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        logging.basicConfig(filename='logs.log',format=LOG_FORMAT,level=logging.INFO, datefmt= DATE_FORMAT)
        logger = logging.getLogger(__name__)
        return logger
    
    @staticmethod
    def get_logger(log_dir="logs", log_name="app.log"):
        # Ensure log directory exists
        os.makedirs(log_dir, exist_ok=True)

        # Full path to log file
        log_path = os.path.join(log_dir, log_name)

        # Create logger
        logger = logging.getLogger("MyAppLogger")
        logger.setLevel(logging.INFO)

        # Avoid adding multiple handlers if called multiple times
        if not logger.handlers:
            # TimedRotatingFileHandler -> new file daily, keep 7 days
            handler = TimedRotatingFileHandler(
                log_path,
                when="midnight",      # rotate at midnight
                interval=1,           # every 1 day
                backupCount=7,        # keep last 7 days of logs
                encoding="utf-8"
        )

        # Log filename format after rotation: app.log.YYYY-MM-DD
        handler.suffix = "%Y-%m-%d"

        # Log format
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

        logger.addHandler(handler)

        return logger