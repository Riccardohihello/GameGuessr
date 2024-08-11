import pygame
from Connection import Connection
from InputManager import InputManager
from Scrollbar import ScrollBar


class Button:
    def __init__(self, x, y, width, height, text, color, textColor, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text, self.color, self.textColor, self.font = text, color, textColor, font

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        textSurface = self.font.render(self.text, True, self.textColor)
        surface.blit(textSurface, textSurface.get_rect(center=self.rect.center))

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)


def load_questions(starting_characters): # funzione per l'assegnazione del contenuto del file "questions.txt"
    with open('questions.txt', 'r') as file:
        text = [line.strip() for line in file if line.strip().startswith(starting_characters)]
    return text if text else print("Error: Invalid file format")


class Client:
    def __init__(self):
        self.username = ""
        self.connection = Connection()
        self.questions = load_questions(('1', '2', '3', '4', '5', '6', '7', '8', '9', '10'))
        self.answers = load_questions(('a', 'b', 'c', 'd'))
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
        domande_scrollbar = ScrollBar(50, 50, width - 100, height - 270, self.questions, pygame.font.Font(None, 22))
        send_button = Button(width // 2 - 100, height - 100, 200, 50, "Invia Domanda", (0, 255, 0), 0, font)
        question_btn_visible = True

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                domande_scrollbar.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and send_button.is_clicked(event.pos):
                    if domande_scrollbar.selected_item is not None:
                        self.connection.send_question(self.questions[domande_scrollbar.selected_item])
                        self.connection.correct_answer = load_questions("risposta:")[domande_scrollbar.selected_item]
                        domande_scrollbar.items.remove(domande_scrollbar.items[domande_scrollbar.selected_item])
                        question_btn_visible = False

            window.fill((240, 240, 240))
            domande_scrollbar.draw(window)
            if question_btn_visible:
                send_button.draw(window)
            pygame.display.flip()

    def run_game(self):  # gestione della logica di gioco (da aggiungere maggiori commenti)
        pygame.init()
        width, height = 640, 480
        window = pygame.display.set_mode((width, height))
        pygame.display.set_caption('What game is this?')

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
        while running:              # logica del gioco (aggiungere maggiori commenti su questa parte una volta finita)
            window.fill((240, 240, 240))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:

                    if game_state == "non connesso" and connect_button_visible and connectButton.is_clicked(event.pos):
                        if len(input_manager.userText) >= 1:
                            self.username = input_manager.userText
                            if self.connection.server_connection():
                                game_state, connect_button_visible = "connesso", False
                                start_button_visible = not self.connection.is_presenter
                        else:
                            self.nickname = "Inserisci un nome prima di connetterti"

                    elif game_state == "connesso" and start_button_visible and startButton.is_clicked(event.pos):
                        if self.connection.connect_to_presenter():
                            game_state, start_button_visible = "partita", False
                    elif game_state == "partita" and self.connection.current_question:
                        for button in self.answer_buttons:
                            if button.is_clicked(event.pos):
                                self.connection.send_answer(f"risposta:{button.text}")

                elif game_state == "non connesso":
                    input_manager.handleEvent(event)

            if game_state == "non connesso":
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

            elif game_state == "partita":
                if self.connection.is_presenter:
                    self.presenter_interface(window, font)
                elif self.connection.current_question:
                    question_text = self.connection.current_question
                    answers = self.get_answers_for_question(int(question_text.split('.')[0]))

                    text = font.render(question_text, True, 0)
                    window.blit(text, (width // 2 - text.get_width() // 2, 50))

                    for button, answer in zip(self.answer_buttons, answers):
                        button.draw(window)
                        answer_text = font.render(answer.strip(), True, 0)
                        window.blit(answer_text, (button.rect.right + 10, button.rect.y + button.rect.height // 2 - answer_text.get_height() // 2))
                else:
                    text = font.render("In attesa della domanda...", True, 0)
                    window.blit(text, (width // 2 - text.get_width() // 2, height // 2))

            pygame.display.flip()
        pygame.quit()


def main():
    Client().run_game()


if __name__ == "__main__":
    main()
