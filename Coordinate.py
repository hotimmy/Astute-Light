#v.0.1.1
import pygame

class Coordinate:
    def __init__(self, font_size):
        self.x = 0
        self.y = 0
        self.font_size = font_size
        self.font = pygame.font.Font(None, font_size)
    
    def set_position(self, x, y):
        self.x = x
        self.y = y
    
    def draw(self, screen):
        screen_width, screen_height = screen.get_size()
        
        # 創建座標標籤
        label_text = f"({self.x}, {self.y})"
        label_surface = self.font.render(label_text, True, (0, 0, 0), (255, 255, 255))
        label_rect = label_surface.get_rect()
        label_rect.topleft = (self.x + 10, self.y + 10)  # 調整標籤在物件右下方一點

        # 檢查並調整標籤位置以避免超出邊界
        if label_rect.right > screen_width:
            label_rect.right = screen_width
        if label_rect.bottom > screen_height:
            label_rect.bottom = screen_height
        
        # 繪製座標標籤
        screen.blit(label_surface, label_rect.topleft)