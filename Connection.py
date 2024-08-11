import socket
import threading


class Connection:
    def __init__(self):
        self.peers = []
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('localhost', 8081)
        self.server_conn = None
        self.is_presenter = False
        self.presenter_addr = None
        self.peer_connections = []
        self.lock = threading.Lock()
        self.current_question = None
        self.correct_answer = None

    def server_connection(self): # funzione per la connessione al server
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

    def listen_for_peers(self): # funzione per l'ascolto dei peers dal peer host
        local_ip, local_port = self.client.getsockname()
        self.client.close()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.client.bind((local_ip, int(local_port)))
        self.client.listen(3)

        print("Presentatore in ascolto su:", local_ip, "porta:", local_port)
        threading.Thread(target=self.accept_peers, daemon=True).start()

    def num_peers(self): # controllo numero peers
        return len(self.peer_connections)

    def accept_peers(self):
        try:
            while len(self.peer_connections) < 3:
                conn, addr = self.client.accept()
                with self.lock:
                    self.peer_connections.append(conn)
                print(f"Peer connesso: {addr}")
                threading.Thread(target=self.handle_peer, args=(conn, addr), daemon=True).start()

            print("Raggiunte 3 connessioni.")
        except Exception as e:
            print(f"Errore nel thread di ascolto: {e}")
        finally:
            self.client.close()

    def connect_to_presenter(self): # funzione per connettersi al peer host
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect(self.presenter_addr)
            self.peer_connections.append(conn)
            print(f"Connected to presenter at {self.presenter_addr}")
            threading.Thread(target=self.handle_peer, args=(conn, self.presenter_addr), daemon=True).start()
            return True
        except Exception as e:
            print(f"Error connecting to presenter: {e}")
            return False

    def handle_peer(self, conn, addr):
        # funzione per l'organizzazione della comunicazione tra peers
        # (da sistemare separandola tra host e peers e magari inserendo le variabili in una classe enum)
        while True:
            try:
                data = conn.recv(1024).decode()
                print(data)
                if not data:
                    break
                elif data == "risposta corretta":
                    print("evvai")
                elif data == "risposta sbagliata":
                    print("nooo")
                elif data.startswith("domanda"):
                    self.current_question = data.strip("domanda")
                elif data.startswith("risposta:"):
                    if self.is_presenter:
                        if self.correct_answer and data.strip() == self.correct_answer:
                            conn.send("risposta corretta".encode())
                        elif self.correct_answer and data.strip() != self.correct_answer:
                            conn.send("risposta sbagliata".encode())
                        else:
                            print("Errore nell'invio della verifica di risposta")
            except Exception as e:
                print(f"Errore gestione del peer {addr}: {e}")
                break
        print(f"connessione persa")
        self.peer_connections.remove(conn)
        conn.close()

    def send_answer(self, answer): # invio risposta al presentatore
        if not self.is_presenter:
            presenter_conn = self.peer_connections[0]
            presenter_conn.send(answer.encode())

    def send_question(self, data): # invio domanda ai peers
        for peer in self.peer_connections:
            try:
                peer.send(("domanda" + data).encode())
            except Exception as e:
                print(f"Errore invio dati al peer: {e}")
