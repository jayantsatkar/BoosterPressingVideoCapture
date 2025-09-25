import logging

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