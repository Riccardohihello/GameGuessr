import random
import socket
import threading


class Player:
    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr


class QuizServer:
    def __init__(self, addr, port):
        self.server = addr
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players = []

    def start(self):
        try:
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.server, self.port))
        except socket.error as e:
            print(str(e))
            return

        self.server_socket.listen(4)
        print("In attesa di una connessione")

        while len(self.players) < 4:
            connection, addr = self.server_socket.accept()
            player = Player(connection, addr)
            self.players.append(player)
            print("Connessione accettata da:", format(addr))

        presenter = random.choice(self.players)
        presenter.conn.send("PRESENTATORE".encode())
        self.players.remove(presenter)

        for player in self.players:
            player.conn.send(f"CONNECT:{presenter.addr[0]}:{presenter.addr[1]}".encode())

        self.server_socket.close()


def main():
    server = QuizServer("127.0.0.1", 8081)
    server.start()


if __name__ == "__main__":
    main()
