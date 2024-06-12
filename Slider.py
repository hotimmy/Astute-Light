import pygame
import sys

class Slider:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.handle_rect = pygame.Rect(x, y, 10, height)
        self.color = (255, 255, 255)
        self.bg_color = (0, 0, 0)
        self.value = 0
        self.dragging = False

    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect)
        pygame.draw.rect(screen, self.color, self.handle_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            print("down")
            if self.handle_rect.collidepoint(event.pos):
                self.dragging = True
                print("slider down")
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self.handle_rect.x = max(self.rect.x, min(event.pos[0], self.rect.x + self.rect.width - self.handle_rect.width))
                self.value = int((self.handle_rect.x - self.rect.x) / (self.rect.width - self.handle_rect.width) * 255)

    def get_value(self):
        return self.value