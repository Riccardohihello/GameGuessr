import socket
import threading

class Peer:
    def __init__(self, conn, nickname):
        self.conn = conn
        self.nickname = nickname
        self.points = 0

    def add_points(self):
        self.points += 10

    def get_stats(self):
        return f"{self.nickname}: {self.points}"


class Connection:
    def __init__(self):
        self.connected_peers = []
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 8081)
        self.is_presenter = False
        self.presenter_addr = None
        self.lock = threading.Lock()
        self.current_question = None
        self.correct_answer = None
        self.nickname = None
        self.points_stats = None


    def set_nick(self, nickname):
        self.nickname = nickname

    def server_connection(self):  # funzione per la connessione al server
        try:
            self.client.connect(self.server_address)
            threading.Thread(target=self.handle_server, args=(), daemon=True).start()
            return True
        except Exception as e:
            print(f"Errore di connessione al server: {e}")
            return False

    def handle_server(self):  # funzione per gestire le risposte del server
        response = self.client.recv(1024).decode()
        if response == "PRESENTATORE":
            self.is_presenter = True
            self.listen_for_peers()
        elif response.startswith("CONNECT:"):
            ip, port = response.strip("CONNECT:").split(":")
            self.presenter_addr = (ip, int(port))
        else:
            print(f"Errore nella ricezione del messaggio")

    def listen_for_peers(self):  # funzione per l'ascolto dei peers dal peer host
        local_ip, local_port = self.client.getsockname()
        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.bind((local_ip, int(local_port)))
        self.client.listen(3)

        print("Presentatore in ascolto su:", local_ip, "porta:", local_port)
        threading.Thread(target=self.accept_peers, daemon=True).start()

    def num_peers(self):  # controllo numero peers
        return len(self.connected_peers)

    def accept_peers(self):
        try:
            while len(self.connected_peers) < 3:
                with self.lock:
                    conn, addr = self.client.accept()
                    nickname = conn.recv(1024).decode() # nella connessione iniziale il peer
                                                        # invia il suo nickname
                    peer = Peer(conn, nickname)
                    self.connected_peers.append(peer)
                    print(f"Peer connesso: {addr}, Nickname: {nickname}")
                threading.Thread(target=self.handle_peers, args=(peer,), daemon=True).start()
                # creazione del thread per gestire la connessione al singolo peer
        except Exception as e:
            print(f"Errore nel thread di ascolto: {e}")
        finally:
            self.client.close()

    def connect_to_presenter(self):  # funzione per connettersi al peer host
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect(self.presenter_addr)
            conn.send(self.nickname.encode())
            peer = Peer(conn, self.nickname)  # creazione di un oggetto Peer per il presentatore
            self.connected_peers.append(peer)
            threading.Thread(target=self.handle_presenter, args=(peer,), daemon=True).start()
            return True
        except Exception as e:
            print(f"Error nella connessione al presentatore: {e}")
            return False

    def handle_presenter(self, peer): #funzione per la gestione dei messaggi inviati dal presenter
        # funzione per l'organizzazione della comunicazione tra peers
        while True:
            try:
                data = peer.conn.recv(1024).decode()
                if not data:
                    break
                elif data == "risposta corretta ricevuta":
                    self.current_question = None
                    self.correct_answer = None
                    self.send_answer("punteggi?")
                elif data == "risposta sbagliata":
                    self.correct_answer = False
                elif data.startswith("domanda"):
                    self.current_question = data.strip("domanda")
                elif data.startswith("Punteggi"):
                    self.points_stats = data.strip("punteggi:")
            except Exception as e:
                print(f"Errore gestione della connessione al presenter: {e}")
                break
        print(f"connessione persa")
        self.connected_peers.remove(peer)
        peer.conn.close()

    def handle_peers(self, peer): #funzione per la gestione dei messaggi inviati dai peers al presenter
        while True:
            try:
                data = peer.conn.recv(1024).decode()
                if not data:
                    break
                elif data.startswith("risposta:") and self.current_question:
                    with self.lock:
                        if self.correct_answer and data.strip() == self.correct_answer:
                            self.current_question = None
                            peer.add_points()
                            self.send_to_peers("risposta corretta ricevuta")
                        elif self.correct_answer and data.strip() != self.correct_answer:
                            peer.conn.send("risposta sbagliata".encode())
                        else:
                            print("Errore nell'invio della verifica di risposta")
                elif data.startswith("punteggi?"):
                    peer.conn.send(self.get_statistics().encode())
                else:
                    print(f"Dati non riconosciuti: {data}")
            except Exception as e:
                print(f"Errore gestione della connessione al peer: {e}")
                break

        print(f"connessione persa")
        self.connected_peers.remove(peer)
        peer.conn.close()

    def send_answer(self, data):  # invio della risposta del peer al presentatore
        if not self.is_presenter:
            presenter_peer = self.connected_peers[0]
            try:
                presenter_peer.conn.send(data.encode())
            except Exception as e:
                print(e)


    def send_to_peers(self, data):  # invio domanda ai peers
        for peer in self.connected_peers:
            try:
                peer.conn.send(data.encode())
            except Exception as e:
                print(f"Errore invio dati al peer: {e}")


    def get_statistics(self): # stringa che raccoglie le statistiche di ogni peer
        stats_list = []
        for peer in self.connected_peers:
            stats_list.append(peer.get_stats())

        stats = "   ".join(stats_list)
        return f"Punteggi: {self.nickname}: P  {stats}"
