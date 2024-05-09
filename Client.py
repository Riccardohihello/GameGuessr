import sys
import pygame
from Connection import Connection


class Client:
    def __init__(self):
        self.points = 0
        self.presentatore = False

        # Implementazione della ricezione della domanda dal server
    def receive_question(self):
        pass

    # implementazione dell'invio della risposta al server
    def send_answer(self):
        return str(self)


def main():

    pygame.init()
    widht, heigth = 640, 480
    window = pygame.display.set_mode((widht, heigth))
    pygame.display.set_caption('What game is it?')

    running = True
    c = Connection()
    clock = pygame.time.Clock()

    background = pygame.Surface(window.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    font = pygame.font.Font(None, 28)
    text = font.render(c.print(), 1, (255, 255, 255))
    textpos = text.get_rect()
    textpos.centerx = background.get_rect().centerx
    background.blit(text, textpos)

    while running:
        clock.tick(60)
        window.blit(background, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()


main()
