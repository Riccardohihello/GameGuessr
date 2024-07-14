import random
import socket
from _thread import start_new_thread


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
        self.presenter = None

        self.questions = self.load_questions(('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'))
        self.answers = self.load_questions(('a', 'b', 'c', 'd'))
        self.correct_answer = self.load_questions('Risposta corretta')

    def load_questions(self, starting_characters):
        # carica le domande dal file questions
        with open('questions.txt', 'r') as file:
            text = []
            for line in file:
                if line.strip().startswith(starting_characters):
                    text.append(line.strip())

            if len(text) > 0:
                return text
            else:
                print("Errore: Formato del file non valido")
                return None

    def start(self):
        try:
            self.server_socket.bind((self.server, self.port))
        except socket.error as e:
            print(str(e))
            return

        self.server_socket.listen(3)
        print("In attesa di una connessione")

        while True:
            connection, addr = self.server_socket.accept()
            print("Connessione accettata da:", format(addr))
            start_new_thread(self.handle_client, (connection, addr))

    def startGame(self):
        # stampa delle domande
        for question in self.questions:
            print(question)

    def handle_client(self, conn, addr):
        player = Player(conn, addr)
        self.players.append(player)

        if len(self.players) >= 3:
            if not self.presenter:
                self.presenter = self.select_presenter()
                print("Presenter selezionato")

        print("conn: ", format(conn))
        conn.send(str.encode("giocatore " + str(len(self.players))))
        while True:
            try:
                received_data = conn.recv(1024)
                received_data = received_data.decode("utf-8")
                if not received_data:
                    print("Disconnesso")
                    break
                elif received_data == "numero giocatori?":
                    conn.send(str.encode(str(len(self.players))))
                elif received_data == "indirizzo ip":
                    if self.presenter:
                        conn.send(str.encode(str(self.presenter.addr[0])))
                    else:
                        conn.send(str.encode("Presenter non ancora selezionato"))
                elif received_data == "porta":
                    if self.presenter:
                        conn.send(str.encode(str(self.presenter.addr[1])))
                    else:
                        conn.send(str.encode("Presenter non ancora selezionato"))
                else:
                    print("ricevuto: ", received_data)

            except:
                break

        print("Connessione persa")
        conn.close()
        self.players.remove(player)

    def select_presenter(self):
        # Seleziona un presentatore casuale tra i giocatori
        presenter = random.choice(self.players)
        print("Il presentatore è il giocatore: " + str(self.players.index(presenter) + 1))
        return presenter


if __name__ == "__main__":
    server = QuizServer("127.0.0.1", 8080)
    server.start()
