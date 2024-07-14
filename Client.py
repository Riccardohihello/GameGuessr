import pygame
from Connection import Connection


class Button:
    def __init__(self, x, y, width, height, text, color, textColor, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.textColor = textColor
        self.font = font

    def draw(self, surface):  # Creazione dei bottoni
        pygame.draw.rect(surface, self.color, self.rect)
        textSurface = self.font.render(self.text, True, self.textColor)
        textRect = textSurface.get_rect(center=self.rect.center)
        surface.blit(textSurface, textRect)

    def isClicked(self, pos):
        return self.rect.collidepoint(pos)


class InputManager:
    def __init__(self, font):
        self.font = font
        self.userText = ["", "", ""]  # Per IP, porta e nome utente
        self.activeInput = 0
        self.inputComplete = [False, False, False]  # valori per il controllo dell'input
        self.maxLengths = [15, 5, 12]  # Lunghezze massime per il testo in input

    def handleEvent(self, event):
        # Gestisce gli eventi di input da tastiera
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.userText[self.activeInput] = self.userText[self.activeInput][:-1]
            elif event.key == pygame.K_RETURN:
                self.inputComplete[self.activeInput] = True
                if self.activeInput < 2:
                    self.activeInput += 1
            elif event.key == pygame.K_TAB:
                self.activeInput = (self.activeInput + 1) % 3
            elif len(self.userText[self.activeInput]) < self.maxLengths[self.activeInput] and not self.inputComplete[
                self.activeInput]:
                self.userText[self.activeInput] += event.unicode

    def draw(self, window, inputRects):
        # Disegna i rettangoli per l'input
        for i in range(3):
            pygame.draw.rect(window, "white", inputRects[i])
            textLevel = self.font.render(self.userText[i], True, "black")
            window.blit(textLevel, (inputRects[i].x + 5, inputRects[i].y + 5))
            if self.activeInput == i:
                cursorX = inputRects[i].x + 5 + self.font.size(self.userText[i])[0]
                pygame.draw.line(window, "black", (cursorX, inputRects[i].y + 5), (cursorX, inputRects[i].y + 25), 2)


def main():
    # Creazione della finestra di gioco
    pygame.init()
    width, height = 640, 480
    window = pygame.display.set_mode((width, height))
    pygame.display.set_caption('What game is this?')

    running = True
    clock = pygame.time.Clock()

    font = pygame.font.Font(None, 28)

    # creazione bottone di connessione
    connectButton = Button(width // 2 - 100, height // 2 - 25, 200, 50, "Connetti", (0, 255, 0), (0, 0, 0), font)

    connectionStatus = ""
    c = None
    gameState = "non connesso"
    presenterIp = ""
    presenterPort = ""

    testi = [
        font.render("Inserire indirizzo IP:", True, "black"),
        font.render("Inserire porta:", True, "black"),
        font.render("Inserire nome:", True, "black")
    ]
    testiRect = [
        testi[0].get_rect(center=(width / 2, 100)),
        testi[1].get_rect(center=(width / 2, 180)),
        testi[2].get_rect(center=(width / 2, 260))
    ]

    inputRects = [
        pygame.Rect(200, 120, 240, 30),
        pygame.Rect(200, 200, 240, 30),
        pygame.Rect(200, 280, 240, 30)
    ]

    inputManager = InputManager(font)

    while running:
        window.fill((240, 240, 240))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if gameState == "non connesso" and connectButton.isClicked(event.pos):
                    try:
                        c = Connection()
                        connectionStatus = "Connessione riuscita!"
                        gameState = "attendendo"
                    except Exception as e:
                        connectionStatus = f"Errore di connessione: {str(e)}"
            elif gameState == "pronto":
                inputManager.handleEvent(event)

        if gameState == "non connesso":
            # Disegna il bottone di connessione
            connectButton.draw(window)
            if connectionStatus:
                statusText = font.render(connectionStatus, True, (255, 0, 0))
                window.blit(statusText, (width // 2 - statusText.get_width() // 2, height // 2 + 50))

        elif gameState == "attendendo":
            waitingText = font.render("Attendi giocatori...", True, (0, 0, 0))
            window.blit(waitingText, (width // 2 - waitingText.get_width() // 2, height // 2))

            if c:
                numPlayers = int(c.send("numero giocatori?"))
                if numPlayers >= 3:
                    gameState = "pronto"
                    presenterIp = c.send("indirizzo ip")
                    presenterPort = c.send("porta")

        elif gameState == "pronto":
            # Disegna i rettangoli di input e i relativi testi
            for i in range(3):
                pygame.draw.rect(window, "blue" if i < 2 else "red", inputRects[i], 2)  # Solo il bordo
                window.blit(testi[i], testiRect[i])

            inputManager.draw(window, inputRects)

            # Stampa l'indirizzo IP e la porta del presenter
            presenterInfoText = font.render(
                f"Presenter IP: {presenterIp}\n Porta: {presenterPort} Stato: {gameState}", True, (0, 0, 0))
            window.blit(presenterInfoText, (width // 2 - presenterInfoText.get_width() // 2, height - 50))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
