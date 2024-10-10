import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from Connection import Connection
from InputManager import InputManager
import Scrollbar

class Button: # rappresentazione dei bottoni dell'interfaccia
    def __init__(self, x, y, width, height, text, color, textColor, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text, self.color, self.textColor, self.font = text, color, textColor, font

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        textSurface = self.font.render(self.text, True, self.textColor)
        surface.blit(textSurface, textSurface.get_rect(center=self.rect.center))

    def change_color(self, new_color):
        self.color = new_color

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def load_questions(starting_characters): # funzione che ritorna il contenuto delle righe del file "questions.txt"
                                        # in base al carattere ricevuto in input
    with open('questions.txt', 'r') as file:
        text = [line.strip() for line in file if line.strip().startswith(starting_characters)]
    return text if text else print("Error: Invalid file format")



def render_wrapped_text(surface, text, font, color, x, y, max_width): # funzione per far rientrare il testo a schermo
    lines = Scrollbar.wrap_text(font, text, max_width)
    text_height = font.size('tg')[0]
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, color)
        surface.blit(text_surface, (x, y + i * (text_height + 5)))
    return len(lines) * (text_height + 5)

class Client:
    def __init__(self):
        self.username = ""
        self.connection = Connection()
        self.questions = load_questions(('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'))
        self.answers = load_questions(('a', 'b', 'c', 'd'))
        self.correct_answers = load_questions("risposta:")
        self.answer_buttons = []
        self.current_question = 0
        self.nickname = ""


    def create_answer_buttons(self, window, font):  # creazione bottoni per le domande
        width, height = window.get_size()
        btn_width, btn_height = 30, 30
        spacing = 15
        x = 50
        y = height // 1.7 - (btn_height * 2 + spacing)
        for i in range(4):
            self.answer_buttons.append(Button(x, y + i * (btn_height + spacing), btn_width, btn_height, chr(97 + i), (0, 200, 0), 0, font))

    def get_answers_for_question(self, question_num):  # gestione dell'indice delle domande
        start_index = (question_num - 1) * 4
        return self.answers[start_index:start_index + 4]

    def presenter_interface(self, window, font): # creazione dell'interfaccia per il peer presentatore
        width, height = window.get_size()
        domande_scrollbar = Scrollbar.Scrollbar(50, 50, width - 100, height - 270, self.questions, pygame.font.Font(None, 22))
        send_button = Button(width // 2 - 100, height - 100, 200, 50, "Invia Domanda", (0, 255, 0), 0, font)

        while True: # gestioni dell'input come la chiusura del gioco o invio della domanda del presenter
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                domande_scrollbar.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and not self.connection.current_question and send_button.is_clicked(event.pos):
                    if domande_scrollbar.selected_item is not None:
                        self.connection.current_question = True
                        self.connection.send_to_peers("domanda" + self.questions[domande_scrollbar.selected_item])
                        self.connection.correct_answer = self.correct_answers[domande_scrollbar.selected_item]
                        self.correct_answers.pop(domande_scrollbar.selected_item)
                        domande_scrollbar.items.remove(domande_scrollbar.items[domande_scrollbar.selected_item])

            window.fill((240, 240, 240))
            domande_scrollbar.draw(window)
            if self.connection.current_question is None:
                send_button.draw(window)

            stats_text = font.render(self.connection.get_statistics(), True, (0, 0, 0))
            window.blit(stats_text, (width // 2 - stats_text.get_width() // 2, 20))

            pygame.display.update()
            pygame.event.pump()


    def run_game(self):  # gestione della logica di gioco
        pygame.init()
        width, height = 640, 480
        window = pygame.display.set_mode((width, height))
        pygame.display.set_caption('GameGuessr')

        font = pygame.font.Font(None, 28)
        connectButton = Button(width // 2 - 100, height // 2 + 50, 200, 50, "Connetti", (0, 255, 0), 0, font)
        startButton = Button(width // 2 - 100, height // 2 + 50, 200, 50, "Inizia", (0, 255, 0), 0, font)

        self.create_answer_buttons(window, font)

        game_state = "non connesso"
        connect_button_visible = True
        start_button_visible = False

        testo = font.render("Inserire nome:", True, "black")
        testo_rect = testo.get_rect(center=(width / 2, height // 2 - 50))
        input_rect = pygame.Rect(width // 2 - 120, height // 2 - 15, 240, 30)
        input_manager = InputManager(font)

        running = True
        while running:          # logica del gioco con gestione iniziale delle fasi di connessione
                                # (connesso al server, connesso al presentatore, in gioco)
            window.fill((240, 240, 240))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if game_state == "non connesso" and connect_button_visible and connectButton.is_clicked(event.pos):
                        if len(input_manager.userText) >= 1:
                            self.connection.set_nick(input_manager.userText)
                            # se viene premuto il bottone per connettersi e la connessione avviene con successo
                            # si passa allo stato successsivo
                            if self.connection.server_connection():
                                game_state, connect_button_visible = "connesso", False
                                start_button_visible = not self.connection.is_presenter
                        elif len(input_manager.userText) == 0:
                            self.nickname = "Inserisci un nome prima di connetterti"

                    elif game_state == "connesso" and start_button_visible and startButton.is_clicked(event.pos):
                        if self.connection.connect_to_presenter():
                            # se la connessione al presentatore ha successo si passa al prossimo stato
                            game_state, start_button_visible = "partita", False
                    elif game_state == "partita" and self.connection.current_question:
                        # nello stato "partita" viene mostrata la domanda se è stata inviata
                        for button in self.answer_buttons:
                            if button.is_clicked(event.pos):
                                self.connection.send_answer(f"risposta:{button.text}")
                                if not self.connection.correct_answer:
                                    button.change_color((200, 0, 0))

                elif game_state == "non connesso":
                    input_manager.handleEvent(event)

            if game_state == "non connesso": # se lo stato è "non connesso" appaiono i bottoni per avviare la connessione
                window.blit(testo, testo_rect)

                input_manager.draw(window, input_rect)
                if connect_button_visible:
                    connectButton.draw(window)
                if self.nickname:
                    statusText = font.render(self.nickname, True, (255, 0, 0))
                    window.blit(statusText, (width // 2 - statusText.get_width() // 2, height // 2 + 100))

            elif game_state == "connesso":
                if self.connection.is_presenter:
                    if self.connection.num_peers() >= 3:
                        game_state = "partita"
                    text = "attendi che tutti i giocatori siano connessi.."
                else:
                    text = "Premi Start per connetterti al presentatore"
                    if start_button_visible and self.connection.presenter_addr:
                        startButton.draw(window)
                text = font.render(text, True, 0)
                window.blit(text, (width // 2 - text.get_width() // 2, height // 2 - 50))

            elif game_state == "partita": # viene disegnata l'interfaccia in base al tipo di utente
                if self.connection.is_presenter:
                    self.presenter_interface(window, font)
                else:
                    if self.connection.current_question:
                        question_text = self.connection.current_question
                        answers = self.get_answers_for_question(int(question_text.split('.')[0]))

                        max_width = width - 100  # Larghezza massima del testo
                        render_wrapped_text(window, question_text, font, 0, 50, 100, max_width)

                        for button, answer in zip(self.answer_buttons, answers):
                            button.draw(window)
                            answer_text = font.render(answer.strip(), True, 0)
                            window.blit(answer_text, (button.rect.right + 10, button.rect.y + button.rect.height // 2 - answer_text.get_height() // 2))
                    else:
                        if not self.connection.correct_answer:
                            for button in self.answer_buttons:
                                if button.color == (200, 0, 0): # il bottone diventa rosso in caso di errore
                                    button.change_color((0, 200, 0))
                        text = font.render("In attesa della domanda...", True, 0)
                        window.blit(text, (width // 2 - text.get_width() // 2, height // 2))

                    stats_text = font.render(self.connection.points_stats, True, 0)
                    window.blit(stats_text, (width // 2 - stats_text.get_width() // 2, 20))

            pygame.display.update()
        pygame.quit()


def main():
    Client().run_game()


if __name__ == "__main__":
    main()
