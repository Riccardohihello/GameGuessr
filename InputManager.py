import pygame


class InputManager:
    def __init__(self, font):
        self.font, self.userText, self.inputComplete = font, "", False
        self.maxLength = 12

    def handleEvent(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.userText = self.userText[:-1]
            elif event.key == pygame.K_RETURN:
                self.inputComplete = True
            elif len(self.userText) < self.maxLength and not self.inputComplete:
                self.userText += event.unicode

    def draw(self, window, inputRect):
        pygame.draw.rect(window, "white", inputRect)
        textLevel = self.font.render(self.userText, True, 0)
        window.blit(textLevel, (inputRect.x + 5, inputRect.y + 5))
        if not self.inputComplete:
            cursX = inputRect.x + 5 + self.font.size(self.userText)[0]
            pygame.draw.line(window, 0, (cursX, inputRect.y + 5), (cursX, inputRect.y + 25), 2)
