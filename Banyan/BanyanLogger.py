import logging


class BanyanLogger:
    @staticmethod
    def getLogger( name, logging_level, filename=None, stdout=True):
        logger = logging.getLogger(name)
        logger.setLevel(logging_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if filename is not None:
            FHandler = logging.FileHandler('peer.log')
            FHandler.setLevel(logging.INFO)
            FHandler.setFormatter(formatter)
            logger.addHandler(FHandler)
        if stdout:
            SHandler = logging.StreamHandler()
            SHandler.setLevel(logging.INFO)
            SHandler.setFormatter(formatter)
            logger.addHandler(SHandler)
        return logger
