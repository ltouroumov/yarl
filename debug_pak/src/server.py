from socketserver import TCPServer, BaseRequestHandler
from threading import Thread
from logging import getLogger, Handler
from http.server import HTTPServer, BaseHTTPRequestHandler
from yarl.package import PackageIndex
from yarl.service import Service

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

class DebugConsoleHandler(BaseRequestHandler):
    def __init__(self):
        self.handler = self.handle_handshake

    def handle_handshake(self, data):
        pass

    def handle(self):
        running = True
        while running:
            data = self.request.recv(1024).strip()
            print("got {} from {}".format(data.decode('utf-8'), self.client_address[0]))
            self.request.sendall(data)


class DebugConsole(Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.port = 32081

    def run(self):
        tcp_server = TCPServer(('localhost', 32081), DebugConsoleHandler)
        tcp_server.serve_forever()
