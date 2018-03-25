import logging


class BanyanLogger:
    @staticmethod
    def get_logger(name, logging_level=logging.INFO, filename="Banyan.log", stdout=False):
        logger = logging.getLogger(name)
        logger.setLevel(logging_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if filename is not None:
            f_handler = logging.FileHandler(filename)
            f_handler.setLevel(logging.INFO)
            f_handler.setFormatter(formatter)
            logger.addHandler(f_handler)
        if stdout:
            s_handler = logging.StreamHandler()
            s_handler.setLevel(logging.INFO)
            s_handler.setFormatter(formatter)
            logger.addHandler(s_handler)
        return logger
