from sfml import sf
from threading import Thread
from logging import getLogger, Handler

logger = getLogger(__name__)

class ConsoleHandler(Handler):
    def __init__(self, console):
        super().__init__()
        self.console = console

    def emit(self, record):
        pass

class DebugConsole(Thread):
    def __init__(self, port):
        self.port = port
        self.socket = None
        super().__init__()

    def send(self, message):
        if self.socket is None:
            return

        self.socket.send(message.encode('utf-8'))

    def run(self):
        try:
            listener = sf.TcpListener()
            listener.listen(self.port)

            self.socket = listener.accept()
            while True:
                self.send("> ")

                buffer = self.socket.receive(64)
                self.send("You sent: %s" % buffer.decode('utf-8'))

        except sf.SocketError as err:
            logger.exception(err)
