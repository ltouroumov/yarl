import asyncio
import websockets

@asyncio.coroutine
def handler(websocket, path):
    print("Handling connection")
    while True:
        message = yield from websocket.recv()
        if message is None:
            print("Connection closed")
            break

        print("Debug {} at {}".format(message, path))
        yield from websocket.send(message)

start_server = websockets.serve(handler, 'localhost', 32081)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
