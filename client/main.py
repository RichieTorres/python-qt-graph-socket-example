import asyncio
import json
import math
import random
from asyncio import transports

delta = math.pi / 8


class SinGenerator:
    def __init__(self):
        self.current = 0

    def get_next_value(self):
        r = math.sin(self.current)
        self.current += delta
        return r


class CosGenerator:
    def __init__(self):
        self.current = 0

    def get_next_value(self):
        r = math.cos(self.current)
        self.current += delta
        return r


class RandomGenerator:
    def get_next_value(self):
        return random.random()


class Control:
    def __init__(self):
        self.current_operation = 'sin'
        self.sin = SinGenerator()
        self.cos = CosGenerator()
        self.random = RandomGenerator()

    def change_operation(self, new_operation):
        self.current_operation = new_operation

    def get_value(self):
        if self.current_operation == 'sin':
            return self.sin.get_next_value()
        if self.current_operation == 'cos':
            return self.cos.get_next_value()
        if self.current_operation == 'random':
            return self.random.get_next_value()


class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport: transports.BaseTransport) -> None:
        print('connection_made')
        self.t = transport

    def data_received(self, data: bytes) -> None:
        print('data_received')
        print(data)
        self.t.write(data)


class ServerProtocol(asyncio.Protocol):
    def __init__(self):
        self.transport = None
        self.control = Control()

    def connection_made(self, transport):
        print('Connection open with the GUI, waiting messages')
        self.transport = transport

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))
        command_received = json.loads(data.decode())

        if command_received['command'] == 'change_operation':
            self.control.change_operation(command_received['operation'])
            self.transport.write(json.dumps({'response': 'change_operation', 'log': 'operation changed'}).encode())
            print('operation changed')

        if command_received['command'] == 'get_value':
            new_value = self.control.get_value()
            self.transport.write(json.dumps({'response': 'get_value', 'value': new_value, 'log': 'value sent'}).encode())
            print('Value sent', new_value)

    def connection_lost(self, exc):
        print('Connection closed')


async def main():
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: ServerProtocol(),
        '127.0.0.1', 65439)

    print('Server is running, waiting GUI commands')
    async with server:
        await server.serve_forever()


asyncio.run(main())
