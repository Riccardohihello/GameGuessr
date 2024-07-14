import socket


class Connection:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"
        self.port = 8080
        self.address = (self.server, self.port)
        self.playerNum = self.connect()

    def connect(self):
        try:
            self.client.connect(self.address)
            return self.client.recv(1024).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            return self.client.recv(1024).decode()
        except socket.error as e:
            print(e)

    def print(self):
        return self.playerNum
