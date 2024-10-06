import pygame

def wrap_text(font, text, max_width):  # funzione per far rientrare il testo nella scrollbar.
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        current_line.append(word)
        text_width = font.size(' '.join(current_line))[0]
        if text_width > max_width:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


class Scrollbar: # scrollbar del presenter
    def __init__(self, x, y, width, height, items, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.items = items
        self.font = font
        self.scroll_offset = 0
        self.selected_item = None
        self.line_height = self.font.get_linesize()
        self.text_offset = 0
        self.item_heights = []

    def draw(self, surface):  # creazione della scrollbar e delle domande contenute all'interno.
        pygame.draw.rect(surface, (200, 200, 200), self.rect)  # Disegna lo sfondo della scrollbar

        current_y = self.rect.y
        self.item_heights = []
        for i, item in enumerate(self.items):
            lines = wrap_text(self.font, item, self.rect.width) # wrapping del testo
            item_height = len(lines) * self.line_height
            self.item_heights.append(item_height)
            y = current_y - self.scroll_offset

            if self.rect.top <= y < self.rect.bottom - item_height:
                item_rect = pygame.Rect(self.rect.x, y, self.rect.width, item_height)
                if i == self.selected_item:
                    pygame.draw.rect(surface, (64, 64, 64), item_rect)  # Evidenziazione dell'elemento selezionato
                    textColor = (255, 255, 255)
                else:
                    textColor = 0
                for j, line in enumerate(lines):
                    text_surface = self.font.render(line, True, textColor)
                    surface.blit(text_surface, (item_rect.x, item_rect.y + j * self.line_height))

            current_y += item_height

    def handle_event(self, event):  # Gestione della selezione e dello scorrere.
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
                self.select_item(event.pos)
        elif event.type == pygame.MOUSEWHEEL:  # regolazione del testo in base alla rotellina
            self.scroll_offset -= event.y * self.line_height
            self.scroll_offset = max(0, min(self.scroll_offset, self.get_max_scroll()))

    def select_item(self, mouse_pos): # Seleziona un elemento in base alla posizione del mouse.
        y_offset = mouse_pos[1] + self.scroll_offset - self.rect.y
        current_y = 0
        for i, item_height in enumerate(self.item_heights):
            if current_y <= y_offset < current_y + item_height:
                self.selected_item = i
                break
            current_y += item_height

    def get_max_scroll(self):  # Calcola il massimo di scorrimento possibile.
        total_height = sum(self.item_heights)
        return max(0, total_height - self.rect.height)
