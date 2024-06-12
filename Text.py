import pygame
import time

class Text:
    def __init__(self, text, font_size, position, color, border_color=(0, 0, 0), border_width=2):
        pygame.font.init()  # 初始化字體模組
        self.text = text
        self.font_size = font_size
        self.position = position
        self.color = color
        self.border_color = border_color
        self.border_width = border_width
        self.font = pygame.font.Font(None, font_size)
        self.rendered_text = self.font.render(text, True, color)
        self.rect = self.rendered_text.get_rect(topleft=position)

    def draw(self, screen):
        # 繪製黑色文字作為邊框
        border_text = self.font.render(self.text, True, self.border_color)
        screen.blit(border_text, (self.position[0] - self.border_width, self.position[1]))
        screen.blit(border_text, (self.position[0] + self.border_width, self.position[1]))
        screen.blit(border_text, (self.position[0], self.position[1] - self.border_width))
        screen.blit(border_text, (self.position[0], self.position[1] + self.border_width))

        # 繪製彩色文字
        screen.blit(self.rendered_text, self.rect)

    def fade_out(self, screen, duration=1):
        start_time = time.time()
        alpha = 255  # 初始透明度為不透明

        fade_surface = self.rendered_text.copy()

        while time.time() - start_time < duration:
            # 計算經過的時間佔總時間的比例
            elapsed_time = time.time() - start_time
            alpha = max(0, 255 * (1 - elapsed_time / duration))  # 逐步減少alpha值

            fade_surface.set_alpha(alpha)  # 設定透明度

            # 清除原來的位置
            
            # 繪製邊框文字
            border_text = self.font.render(self.text, True, self.border_color)
            border_text.set_alpha(alpha)
            screen.blit(border_text, (self.position[0] - self.border_width, self.position[1]))
            screen.blit(border_text, (self.position[0] + self.border_width, self.position[1]))
            screen.blit(border_text, (self.position[0], self.position[1] - self.border_width))
            screen.blit(border_text, (self.position[0], self.position[1] + self.border_width))

            # 繪製淡出的文字
            screen.blit(fade_surface, self.rect)

            pygame.display.update()
            pygame.time.delay(10)  # 延遲一段時間，達到平滑過渡效果
