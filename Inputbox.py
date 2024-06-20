#v.0.1.1
import pygame
import re

class Inputbox:
    def __init__(self, x, y, width, height, label='', font_size=24, default_text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (0, 0, 0)
        self.bg_color = (255, 255, 255)
        self.text = ''
        self.default_text = default_text
        self.font = pygame.font.Font(None, font_size)
        self.active = False
        self.label = label
        self.error_message = ''
        self.label_surface = self.font.render(self.label, True, self.color)
        self.placeholder_color = (150, 150, 150)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 如果點擊輸入框內部，則激活輸入框；否則，失去焦點
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # 改變顏色
            self.color = (0, 0, 0) if self.active else (0, 0, 0)
        
        if event.type == pygame.KEYUP or event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def check_number(self):
        if not self.text.isdigit() and self.text != '':
            self.error_message = 'Error: Not a number'
        else:
            self.error_message = ''
    
    def check_ip(self):
        dot_count = self.text.count('.')
        if dot_count != 3 or not all(part.isdigit() and 0 <= int(part) <= 255 for part in self.text.split('.')):
            self.error_message = 'Error: Not a valid IP'
        else:
            self.error_message = ''

    def draw(self, screen):
        # 填充背景
        pygame.draw.rect(screen, self.bg_color, self.rect)
        
        # 繪製文本或佔位符
        if self.text or self.active:
            text_surface = self.font.render(self.text, True, self.color)
        else:
            text_surface = self.font.render(self.default_text, True, self.placeholder_color)
        
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        # 繪製輸入框的邊界
        pygame.draw.rect(screen, self.color, self.rect, 2)
        
        # 繪製標籤
        screen.blit(self.label_surface, (self.rect.x - self.label_surface.get_width() - 10, self.rect.y + 5))
        
        # 繪製錯誤信息
        if self.error_message:
            error_surface = self.font.render(self.error_message, True, (255, 0, 0))
            error_rect = error_surface.get_rect(topleft=(self.rect.x, self.rect.bottom + 5))
            screen.blit(error_surface, error_rect)
        
    def get_text(self):
        return self.text if self.text else self.default_text

    def set_text(self, new_text):
        self.text = new_text
