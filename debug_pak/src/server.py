from threading import Thread
from logging import getLogger, Handler
from http.server import HTTPServer, BaseHTTPRequestHandler
from yarl.package import PackageIndex
from yarl.service import Service
import websockets
import asyncio

logger = getLogger(__name__)
package = Service.get('engine.package_loader').get_from_module(__name__)

class PackagedRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logger.info("Getting %s", self.path)
        self.send_header("Content-Type", "text/html")

        if self.path == '/':
            resource_name = 'web/console.html'
        else:
            resource_name = 'web' + self.path

        if package.contains(resource_name, PackageIndex.RESOURCE):
            handle, meta = package.read(resource_name, PackageIndex.RESOURCE)
            self.wfile.write(handle)
            self.send_response(200, "OK")
        else:
            self.send_error(404, "Resource Not Found")

class ConsoleHandler(Handler):
    def __init__(self, console):
        super().__init__()
        self.console = console

    def emit(self, record):
        pass

class ConsoleWebInterface(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.port = 32080

    def run(self):
        http_server = HTTPServer(server_address=('127.0.0.1', self.port),
                                 RequestHandlerClass=PackagedRequestHandler)
        logger.info("Serving console to http://localhost:%s", self.port)
        http_server.serve_forever()

class DebugConsole(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.port = 32081

        self.loop = asyncio.get_event_loop()
        self.path_handlers = {
            '/rcon': self.rcon_handler,
            '/repl': self.repl_handler,
            '/log': self.log_handler
        }

    @asyncio.coroutine
    def rcon_handler(self, websocket):
        yield from websocket.send("""{"packet_type": "rcon", "payload": "[[b;#00BF00;]RCON Online]"}""")
        while True:
            message = yield from websocket.recv()
            if message is None:
                break

            yield from websocket.send(message)

    @asyncio.coroutine
    def repl_handler(self, websocket):
        yield from websocket.send("""{"packet_type": "rcon", "payload": "[[b;#00BF00;]REPL Online]"}""")
        while True:
            message = yield from websocket.recv()
            if message is None:
                break

            yield from websocket.send(message)

    @asyncio.coroutine
    def log_handler(self, websocket):
        while True:
            yield from asyncio.sleep(10)

            response = """{"packet_type": "log", "payload": "Log entry"}"""
            yield from websocket.send(response)

    @asyncio.coroutine
    def handler(self, websocket, path):
        if path in self.path_handlers:
            handler = self.path_handlers[path]
            yield from handler(websocket)
        else:
            while True:
                yield from websocket.recv()
                yield from websocket.send("Unkown channel")

    def run(self):
        start_server = websockets.serve(self.handler, 'localhost', 32081)
        asyncio.set_event_loop(self.loop)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
