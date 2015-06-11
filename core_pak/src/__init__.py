import logging
logger = logging.getLogger(__name__)

class Bootstrap:
    def __init__(self):
        pass

    def init(self):
        logger.info("Boostrap of %s", type(self))
