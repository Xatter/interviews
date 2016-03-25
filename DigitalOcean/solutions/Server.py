import socket
import select
from typing import List
import queue
import logging
import os

LOG_LEVEL = os.getenv('DO_LOG_LEVEL')
if LOG_LEVEL == "DEBUG":
    LOG_LEVEL = logging.DEBUG
elif LOG_LEVEL == "INFO":
    LOG_LEVEL = logging.INFO
elif LOG_LEVEL == "WARN":
    LOG_LEVEL = logging.WARN
else:
    LOG_LEVEL = logging.INFO

PORT = os.getenv('DO_PORT') or 8080

logging.basicConfig(level=LOG_LEVEL,
                    filename='service.log',
                    format="%(name)s: %(message)s")

OK = "OK\n"
FAIL = "FAIL\n"
ERROR = "ERROR\n"


class Indexer(object):
    def __init__(self):
        self.INDEX = {}
        self.INVERSE_INDEX = {}
        self.logger = logging.getLogger("Indexer")

    def decode(self, message:str):
        if message.count('|') < 2:
            return ('ERROR', 'Must be two pipes', None)

        parts = message.split('|')

        if ',' in parts[1]:
            return ('ERROR', 'Can not have commas in package field', None)

        dependencies = parts[2].split(',')
        if dependencies == ['']:
            dependencies = None

        return (parts[0], parts[1], dependencies)

    def index(self, package:str, dependencies:List[str]):
        self.logger.debug("INDEX (%s) Dependencies (%s)", package, dependencies)
        if package in self.INDEX:
            return OK

        if dependencies is not None:
            for dependency in dependencies:
                if dependency not in self.INDEX:
                    return FAIL

                if dependency not in self.INVERSE_INDEX:
                    self.INVERSE_INDEX[dependency] = {}

                self.INVERSE_INDEX[dependency][package] = None

        self.INDEX[package] = dependencies
        self.logger.info("Package Indexed (%s)", package)
        return OK

    def remove(self, package:str):
        self.logger.debug("REMOVE (%s)", package)
        if package not in self.INDEX:
            return OK

        if package in self.INVERSE_INDEX:
            self.logger.error("Could not remove package (%s) because it is depended upon by (%s)", package, [k for k in self.INVERSE_INDEX[package]])
            return FAIL

        keys = [k for k in self.INVERSE_INDEX]
        for k in keys:
            dependsUpon = self.INVERSE_INDEX[k]
            if package in dependsUpon:
                del dependsUpon[package]

            if len(dependsUpon) == 0:
                del self.INVERSE_INDEX[k]

        del self.INDEX[package]
        self.logger.info("Package Removed (%s)", package)
        return OK

    def query(self, package:str):
        self.logger.debug("QUERY (%s)", package)
        if package in self.INDEX:
            return OK
        else:
            return FAIL

indexer = Indexer()

if __name__ == '__main__':
    # This code is very procedural, but also easy to understand since it reads completely from
    # top to bottom, left to right. I would hesitate to use an object oriented abstraction until
    # it's absolutely necessary.

    # A good functional abstraction would be AsyncSequence

    logger = logging.getLogger("Server")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind(('localhost', PORT))
    server.listen(10)

    inputs = [server]
    outputs = []
    message_queues = {}

    while inputs:
        ready_to_read, ready_to_write, exceptional = select.select(inputs, outputs, [])

        for s in ready_to_read:
            if s is server:
                connection, client_address = s.accept()
                connection.setblocking(0)
                inputs.append(connection)

                message_queues[connection] = queue.Queue()
                logger.info("Client connected (%s)", client_address)
            else:
                logger.debug("Client Socket (%s)", s)
                data = s.recv(1024) # what if there's more data?
                logger.debug("Recieved data(%s)", data)
                if data:
                    # Design notes:
                    # We could make a more general abstraction here to make it easier to encapsulate
                    # this logic with threads or some other mechanism. This would be a good enhancement
                    # if/when the performance is not good enough, but add lots of compexity around synchronization
                    # even with a nice abstraction such as Tasks, asyncio, etc.
                    # For now, I like the readability that all the code and it's calls are in one place
                    # and not strewn all over the file (or worse multiple files)
                    message = data.decode('utf-8').strip()
                    result = ERROR

                    command, package, dependencies = indexer.decode(message)

                    logger.debug("Parsed (%s, %s, %s)", command, package, dependencies)

                    if command == "INDEX":
                        result = indexer.index(package, dependencies)
                    elif command == "REMOVE":
                        result = indexer.remove(package)
                    elif command == "QUERY":
                        result = indexer.query(package)
                    else:
                        logger.error("Parsing Error (%s) (%s)", message, package)

                    logger.debug("Response (%s)", result)
                    message_queues[s].put(result)
                    if s not in outputs:
                        outputs.append(s)
                else:
                    if s in outputs:
                        outputs.remove(s)

                    inputs.remove(s)
                    s.close()
                    del message_queues[s]

        for s in ready_to_write:
            try:
                next_msg = message_queues[s].get_nowait()
            except queue.Empty:
                outputs.remove(s)
            except KeyError:
                pass
            else:
                s.send(next_msg.encode('utf-8'))

        for s in exceptional:
            inputs.remove(s)
            if s in outputs:
                outputs.remove(s)
            s.close()

            del message_queues[s]
