import pygame
import random
import sys
from pygame.locals import *

# Game Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
FPS = 32
PIPE_GAP = 150

# Asset paths
PIPE_IMAGE = 'images/pipe.png'
BACKGROUND_IMAGE = 'images/background.jpg'
BIRD_IMAGE = 'images/bird.png'
BASE_IMAGE = 'images/base.jfif'

# Sprite sizes
BIRD_WIDTH = 40
BIRD_HEIGHT = 30
PIPE_WIDTH = 70
PIPE_HEIGHT = 400

# Debug mode pentru vizualizarea hitbox-urilor
DEBUG = False

class FlappyBird:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Flappy Bird')
        self.clock = pygame.time.Clock()
        
        self.images = {}
        self.load_images()
        self.reset_game()
    
    def reset_game(self):
        self.bird_y = int(WINDOW_HEIGHT/2)
        self.bird_x = int(WINDOW_WIDTH/5)
        self.base_y = int(WINDOW_HEIGHT * 0.8)
        self.bird_movement = 0
        self.gravity = 0.25
        self.jump_height = -7
        self.game_active = False
        self.score = 0
        self.pipes = []
        self.spawn_pipe()
        self.spawn_pipe()
    
    def load_images(self):
        bird_img = pygame.image.load(BIRD_IMAGE).convert_alpha()
        self.images['bird'] = pygame.transform.scale(bird_img, (BIRD_WIDTH, BIRD_HEIGHT))
        
        bg_img = pygame.image.load(BACKGROUND_IMAGE).convert_alpha()
        self.images['bg'] = pygame.transform.scale(bg_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
        
        base_img = pygame.image.load(BASE_IMAGE).convert_alpha()
        self.images['base'] = pygame.transform.scale(base_img, (WINDOW_WIDTH, 100))
        
        pipe_img = pygame.image.load(PIPE_IMAGE).convert_alpha()
        self.images['pipe'] = pygame.transform.scale(pipe_img, (PIPE_WIDTH, PIPE_HEIGHT))
        self.images['pipe_inverted'] = pygame.transform.rotate(
            pygame.transform.scale(pipe_img, (PIPE_WIDTH, PIPE_HEIGHT)),
            180
        )
    
    def spawn_pipe(self):
        if not self.pipes:
            pipe_x = WINDOW_WIDTH
        else:
            pipe_x = self.pipes[-1]['bottom']['x'] + 300
        
        # Ajustăm înălțimea țevilor pentru a asigura un spațiu consistent de trecere
        bottom_height = random.randint(
            int(self.base_y - PIPE_HEIGHT * 0.6),  # Minimum height
            int(self.base_y - PIPE_GAP - 50)  # Maximum height
        )
        
        new_pipe = {
            'bottom': {'x': pipe_x, 'height': bottom_height},
            'top': {'x': pipe_x, 'height': bottom_height - PIPE_GAP - PIPE_HEIGHT},
            'scored': False
        }
        self.pipes.append(new_pipe)
    
    def move_pipes(self):
        for pipe in self.pipes:
            pipe['bottom']['x'] -= 4
            pipe['top']['x'] -= 4
        
        self.pipes = [pipe for pipe in self.pipes if pipe['bottom']['x'] > -PIPE_WIDTH]
        
        if not self.pipes or self.pipes[-1]['bottom']['x'] < WINDOW_WIDTH - 300:
            self.spawn_pipe()
    
    def get_bird_rect(self):
        # Reducem hitbox-ul păsării pentru a fi mai precis
        bird_hitbox_margin = 5
        return pygame.Rect(
            self.bird_x + bird_hitbox_margin,
            self.bird_y + bird_hitbox_margin,
            BIRD_WIDTH - 2 * bird_hitbox_margin,
            BIRD_HEIGHT - 2 * bird_hitbox_margin
        )
    
    def get_pipe_rects(self, pipe):
        # Reducem hitbox-ul țevilor pentru a fi mai permisiv
        pipe_hitbox_margin = 5
        top_rect = pygame.Rect(
            pipe['top']['x'] + pipe_hitbox_margin,
            0,
            PIPE_WIDTH - 2 * pipe_hitbox_margin,
            abs(pipe['top']['height'])
        )
        
        bottom_rect = pygame.Rect(
            pipe['bottom']['x'] + pipe_hitbox_margin,
            pipe['bottom']['height'],
            PIPE_WIDTH - 2 * pipe_hitbox_margin,
            WINDOW_HEIGHT - pipe['bottom']['height']
        )
        
        return top_rect, bottom_rect
    
    def check_collision(self):
        if self.bird_y >= self.base_y - BIRD_HEIGHT or self.bird_y <= 0:
            return True
            
        bird_rect = self.get_bird_rect()
        
        for pipe in self.pipes:
            top_rect, bottom_rect = self.get_pipe_rects(pipe)
            
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                return True
        return False
    
    def update_score(self):
        for pipe in self.pipes:
            if not pipe['scored'] and pipe['bottom']['x'] + PIPE_WIDTH < self.bird_x:
                self.score += 1
                pipe['scored'] = True
    
    def draw_hitboxes(self):
        if not DEBUG:
            return
            
        # Desenează hitbox-ul păsării
        bird_rect = self.get_bird_rect()
        pygame.draw.rect(self.screen, (255, 0, 0), bird_rect, 1)
        
        # Desenează hitbox-urile țevilor
        for pipe in self.pipes:
            top_rect, bottom_rect = self.get_pipe_rects(pipe)
            pygame.draw.rect(self.screen, (255, 0, 0), top_rect, 1)
            pygame.draw.rect(self.screen, (255, 0, 0), bottom_rect, 1)
    
    def draw(self):
        self.screen.blit(self.images['bg'], (0, 0))
        
        for pipe in self.pipes:
            self.screen.blit(self.images['pipe_inverted'], (pipe['top']['x'], pipe['top']['height']))
            self.screen.blit(self.images['pipe'], (pipe['bottom']['x'], pipe['bottom']['height']))
        
        self.screen.blit(self.images['base'], (0, self.base_y))
        
        rotation = min(max(-90, -self.bird_movement * 3), 30)
        rotated_bird = pygame.transform.rotate(self.images['bird'], rotation)
        self.screen.blit(rotated_bird, (self.bird_x, self.bird_y))
        
        font = pygame.font.Font(None, 50)
        score_surface = font.render(str(self.score), True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(WINDOW_WIDTH/2, 50))
        self.screen.blit(score_surface, score_rect)
        
        self.draw_hitboxes()  # Desenează hitbox-urile în modul debug
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                
                if event.type == KEYDOWN:
                    if event.key == K_SPACE and not self.game_active:
                        self.reset_game()
                        self.game_active = True
                    elif event.key == K_SPACE and self.game_active:
                        self.bird_movement = self.jump_height
                    # Adăugăm posibilitatea de a activa/dezactiva modul debug cu tasta D
                    elif event.key == K_d:
                        global DEBUG
                        DEBUG = not DEBUG
            
            if self.game_active:
                self.bird_movement += self.gravity
                self.bird_y += self.bird_movement
                self.move_pipes()
                
                if self.check_collision():
                    self.game_active = False
                
                self.update_score()
            
            self.draw()
            pygame.display.update()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = FlappyBird()
    game.run()