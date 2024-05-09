import random
import socket
from _thread import start_new_thread


def load_questions(starting_character):
    with open('questions.txt', 'r') as file:
        text = []
        for line in file:
            if line.strip().startswith(starting_character):
                text.append(line.strip())

        if len(text) > 0:
            return text
        else:
            print("Error: Invalid question format in questions.txt")
            return None


class QuizServer:
    def __init__(self, addr, port):
        self.server = addr
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.players = []
        self.presentatore = None

        self.questions = load_questions(('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'))
        self.answers = load_questions(('a', 'b', 'c', 'd'))
        self.correct_answer = load_questions('Risposta corretta')

    def start(self):
        try:
            self.server_socket.bind((self.server, self.port))
        except socket.error as e:
            print(str(e))
            return

        self.server_socket.listen(3)
        print("Waiting for a connection")

        while True:
            connection, addr = self.server_socket.accept()
            print("Accepted connection to:", format(addr))
            start_new_thread(self.handle_client, (connection,))

            if len(self.players) >= 3:
                self.presentatore = self.select_presenter()

    def startGame(self):
        for question in self.questions:
            print(question)

            # msg = question.encode()
            # self.server_socket.send(msg)

            # answer = self.server_socket.recv(1024).decode()
            # print(answer)

    def handle_client(self, conn):
        self.players.append(conn)
        conn.send(str.encode("player " + str(len(self.players))))
        while True:
            try:
                received_data = conn.recv(1024)

                if not received_data:
                    print("Disconnected")
                    break
                else:
                    print("ricevuto: ", received_data)
            except:
                break

        print("Connection lost")
        conn.close()
        self.players.remove(conn)

    def select_presenter(self):
        presenter = random.choice(self.players)
        print("The presenter is:", presenter)
        return presenter


if __name__ == "__main__":
    server = QuizServer("127.0.0.1", 8080)
    server.start()
