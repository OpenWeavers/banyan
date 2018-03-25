import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler
FHandler = logging.FileHandler('peer.log')
FHandler.setLevel(logging.INFO)

SHandler = logging.StreamHandler()
SHandler.setLevel(logging.INFO)

# create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
FHandler.setFormatter(formatter)
SHandler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(FHandler)
logger.addHandler(SHandler)
