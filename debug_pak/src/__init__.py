import logging
from yarl.service import Service
from yarl.debug.server import ConsoleWebInterface, DebugConsole

logger = logging.getLogger(__name__)

class Bootstrap(object):
    thread_runner = Service('engine.thread_runner')

    def __init__(self):
        pass

    def init(self):
        logger.info("Boostrap of %s", type(self))

        self.thread_runner.register(ConsoleWebInterface())
        self.thread_runner.register(DebugConsole())
