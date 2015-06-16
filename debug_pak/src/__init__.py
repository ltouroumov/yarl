import logging
from yarl.service import Service
from yarl.debug.server import ConsoleWebInterface, DebugConsoleServer, ConsoleHandler
from yarl.debug.repl import DebugInterpreter

logger = logging.getLogger(__name__)


def websocket_filter(record):
    return record.name not in ['websockets.protocol', 'yarl.debug.server']


class Bootstrap(object):
    container = Service('service_container')
    thread_runner = Service('engine.thread_runner')

    def __init__(self):
        pass

    def init(self):
        logger.info("Boostrap of %s", type(self))

        debug_handler = ConsoleHandler()
        debug_handler.setFormatter(Service.get('engine.default_formatter'))
        debug_handler.addFilter(websocket_filter)
        self.container.add_instance('debug.console_handler', debug_handler)

        self.container.add_factory('debug.interpreter', DebugInterpreter)

        root_logger = logging.getLogger()
        root_logger.addHandler(debug_handler)

        self.thread_runner.register(ConsoleWebInterface())
        self.thread_runner.register(DebugConsoleServer())
