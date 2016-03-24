import socket
from typing import List

OK = "OK\n"
FAIL = "FAIL\n"
ERROR = "ERROR\n"

class Server(object):
    def __init__(self):
        self.INDEX = {}
        self.INVERSE_INDEX = {}

    def decode(self, message:str):
        if message[-1] != '\n':
           return None

        message = message[:-1]
            
        parts = message.split('|')
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

    def begin(self):
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind(('localhost', 8080))
        serversocket.listen(5)

        while True:
            (clientsocket, address) = serversocket.accept()
            ct = client_thread(clientsocket)
            ct.run()

if __name__ == '__main__':
    s = Server()
    s.begin()
