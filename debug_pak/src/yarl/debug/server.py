from io import StringIO
from threading import Thread
from logging import getLogger, Handler
from http.server import HTTPServer, BaseHTTPRequestHandler
import sys
from yarl.package import PackageIndex
from yarl.service import Service
from collections import deque
import json
import websockets
import asyncio

logger = getLogger(__name__)
package = Service.get('engine.package_loader').get_from_module(__name__)


class ConsoleHandler(Handler):
    max_records = 200

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.records = deque(maxlen=self.max_records)

    def emit(self, record):
        self.records.append(record)

    def flush(self):
        pending = list(map(self.format, self.records))
        self.records.clear()
        return pending


class PackagedRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logger.info("Getting %s", self.path)

        if self.path == '/':
            resource_name = 'web/console.html'
        else:
            resource_name = 'web' + self.path

        logger.debug("Resource: %s", resource_name)
        if package.contains(resource_name, PackageIndex.RESOURCE):
            logger.debug("Sending resource")
            handle, meta = package.read(resource_name, PackageIndex.RESOURCE)
            self.send_response(200, "OK")
            self.end_headers()
            self.wfile.write(handle)
        else:
            logger.debug("Resource not found")
            self.send_error(404, "Resource Not Found")

        logger.debug("GET DONE")


class ConsoleWebInterface(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.port = 32080

    def run(self):
        http_server = HTTPServer(server_address=('127.0.0.1', self.port),
                                 RequestHandlerClass=PackagedRequestHandler)
        logger.info("Serving console to http://localhost:%s", self.port)
        http_server.serve_forever()


class DebugConsoleServer(Thread):
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

            yield from websocket.send("""{"packet_type": "rcon", "payload": "{!r}"}""".format(message))

    @asyncio.coroutine
    def repl_handler(self, websocket):
        interpreter = Service.get('debug.interpreter')
        yield from websocket.send("""{"packet_type": "repl", "payload": "[[b;#00BF00;]REPL Online]"}""")
        while True:
            message = yield from websocket.recv()
            if message is None:
                break

            data = json.loads(message)
            repl = data['message']['repl']
            code = data['message']['code']
            if repl:
                out_str = interpreter.run_repl(code)
            else:
                out_str = interpreter.run_code(code)

            message = json.dumps({
                "packet_type": "repl",
                "payload": out_str
            })
            yield from websocket.send(message)

    @asyncio.coroutine
    def log_handler(self, websocket):
        log_queue = Service.get('debug.console_handler')
        yield from websocket.send("""{"packet_type": "rcon", "payload": "[[b;#00BF00;]LOG Online]"}""")
        while True:
            entries = log_queue.flush()
            if len(entries) > 0:
                response = json.dumps({
                    "packet_type": "log",
                    "payload": entries
                })
                yield from websocket.send(response)

            yield from asyncio.sleep(0.5)

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
        asyncio.set_event_loop(self.loop)

        start_server = websockets.serve(self.handler, 'localhost', 32081)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()
