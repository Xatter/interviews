import socket
import select
from typing import List
import queue

OK = "OK\n"
FAIL = "FAIL\n"
ERROR = "ERROR\n"

class Indexer(object):
    def __init__(self):
        self.INDEX = {}
        self.INVERSE_INDEX = {}

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
        return OK

    def remove(self, package:str):
        if package not in self.INDEX:
            return OK

        if package in self.INVERSE_INDEX:
            return FAIL

        keys = [k for k in self.INVERSE_INDEX]
        for k in keys:
            dependsUpon = self.INVERSE_INDEX[k]
            if package in dependsUpon:
                dependsUpon.pop(package, None)

            if len(dependsUpon) == 0:
                self.INVERSE_INDEX.pop(k, None)

        self.INDEX.pop(package, None)
        return OK

    def query(self, package:str):
        if package in self.INDEX:
            return OK
        else:
            return FAIL

indexer = Indexer()

if __name__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setblocking(0)
    server.bind(('localhost', 8080))
    server.listen(10)

    inputs = [ server ]
    outputs = [ ]
    message_queues = {}


    while inputs:
        ready_to_read, ready_to_write, exceptional = select.select(inputs, outputs, [])

        for s in ready_to_read:
            if s is server:
                connection, client_address = s.accept()
                connection.setblocking(0)
                inputs.append(connection)

                message_queues[connection] = queue.Queue()
            else:
                data = s.recv(1024)
                print(s)
                print(data)
                if data:
                    message = data.decode('utf-8').strip()
                    result = ERROR

                    command, package, dependencies = indexer.decode(message)

                    print(command)
                    print(package)
                    print(dependencies)

                    if command == "INDEX":
                        result = indexer.index(package, dependencies)
                    elif command == "REMOVE":
                        result = indexer.remove(package)
                    elif command == "QUERY":
                        result = indexer.query(package)

                    print(result)
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


