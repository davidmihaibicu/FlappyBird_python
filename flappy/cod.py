import pygame
import random
import sys
from pygame.locals import *

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 500
FPS = 60
PIPE_GAP = 150
HIGHSCORE_FILE = 'highscore.txt'

PIPE_IMAGE = 'images/pipe.png'
BACKGROUND_IMAGE = 'images/upb.jpeg'
BIRD_IMAGE = 'images/bird.png'
BASE_IMAGE = 'images/base.jfif'

BIRD_WIDTH = 40
BIRD_HEIGHT = 30
PIPE_WIDTH = 70
PIPE_HEIGHT = 320

class FlappyBird:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption('Flappy Bird')
        self.clock = pygame.time.Clock()
        
        self.images = {}
        self.load_images()
        self.load_highscore()
        self.reset_game()
    
    def load_highscore(self):
        try:
            with open(HIGHSCORE_FILE, 'r') as f:
                self.highscore = int(f.read().strip())
        except:
            self.highscore = 0
    
    def save_highscore(self):
        try:
            with open(HIGHSCORE_FILE, 'w') as f:
                f.write(str(self.highscore))
        except:
            print("Nu s-a putut salva high score-ul")
    
    def reset_game(self):
        self.bird_y = int(WINDOW_HEIGHT/2)
        self.bird_x = int(WINDOW_WIDTH/5)
        self.base_y = int(WINDOW_HEIGHT * 0.8)
        self.bird_movement = 0
        self.gravity = 0.5
        self.jump_height = -8
        self.game_active = False
        self.score = 0
        self.pipes = []
        self.spawn_pipe()
        self.spawn_pipe()
    
    def load_images(self):
        try:
            bird_img = pygame.image.load(BIRD_IMAGE).convert_alpha()
            self.images['bird'] = pygame.transform.scale(bird_img, (BIRD_WIDTH, BIRD_HEIGHT))
            
            bg_img = pygame.image.load(BACKGROUND_IMAGE).convert()
            self.images['bg'] = pygame.transform.scale(bg_img, (WINDOW_WIDTH, WINDOW_HEIGHT))
            
            base_img = pygame.image.load(BASE_IMAGE).convert()
            self.images['base'] = pygame.transform.scale(base_img, (WINDOW_WIDTH, 100))
            
            pipe_img = pygame.image.load(PIPE_IMAGE).convert_alpha()
            self.images['pipe'] = pygame.transform.scale(pipe_img, (PIPE_WIDTH, PIPE_HEIGHT))
            self.images['pipe_inverted'] = pygame.transform.rotate(
                pygame.transform.scale(pipe_img, (PIPE_WIDTH, PIPE_HEIGHT)),
                180
            )
        except pygame.error as e:
            print(f"Eroare la încărcarea imaginilor: {e}")
            sys.exit(1)
    
    def spawn_pipe(self):
        if not self.pipes:
            pipe_x = WINDOW_WIDTH
        else:
            pipe_x = self.pipes[-1]['bottom']['x'] + 300
        
        bottom_height = random.randint(
            int(WINDOW_HEIGHT * 0.4),
            int(WINDOW_HEIGHT * 0.6)
        )
        
        new_pipe = {
            'bottom': {'x': pipe_x, 'height': bottom_height},
            'top': {'x': pipe_x, 'height': bottom_height - PIPE_GAP - PIPE_HEIGHT},
            'scored': False
        }
        self.pipes.append(new_pipe)
    
    def move_pipes(self):
        pipe_speed = 3
        for pipe in self.pipes:
            pipe['bottom']['x'] -= pipe_speed
            pipe['top']['x'] -= pipe_speed
        
        self.pipes = [pipe for pipe in self.pipes if pipe['bottom']['x'] > -PIPE_WIDTH]
        
        if not self.pipes or self.pipes[-1]['bottom']['x'] < WINDOW_WIDTH - 300:
            self.spawn_pipe()
    
    def check_collision(self):
        bird_rect = pygame.Rect(
            self.bird_x + 10,
            self.bird_y + 10,
            BIRD_WIDTH - 20,
            BIRD_HEIGHT - 20
        )
        
        if self.bird_y >= self.base_y - BIRD_HEIGHT or self.bird_y <= 0:
            return True
        
        for pipe in self.pipes:
            margin = 15
            
            top_rect = pygame.Rect(
                pipe['top']['x'] + margin,
                0,
                PIPE_WIDTH - (2 * margin),
                pipe['top']['height'] + PIPE_HEIGHT
            )
            
            bottom_rect = pygame.Rect(
                pipe['bottom']['x'] + margin,
                pipe['bottom']['height'],
                PIPE_WIDTH - (2 * margin),
                WINDOW_HEIGHT - pipe['bottom']['height']
            )
            
            if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
                if (bird_rect.right > top_rect.left + 5 and 
                    bird_rect.left < top_rect.right - 5):
                    return True
        
        return False
    
    def update_score(self):
        for pipe in self.pipes:
            if not pipe['scored'] and pipe['bottom']['x'] + PIPE_WIDTH < self.bird_x:
                self.score += 1
                if self.score > self.highscore:
                    self.highscore = self.score
                    self.save_highscore()
                pipe['scored'] = True
    
    def draw(self):
        self.screen.blit(self.images['bg'], (0, 0))
        
        for pipe in self.pipes:
            self.screen.blit(self.images['pipe'], 
                           (pipe['bottom']['x'], pipe['bottom']['height']))
            self.screen.blit(self.images['pipe_inverted'], 
                           (pipe['top']['x'], pipe['top']['height']))
        
        self.screen.blit(self.images['base'], (0, self.base_y))
        
        rotation = min(max(-90, -self.bird_movement * 3), 30)
        rotated_bird = pygame.transform.rotate(self.images['bird'], rotation)
        self.screen.blit(rotated_bird, (self.bird_x, self.bird_y))
        
        font = pygame.font.Font(None, 50)
        
        score_surface = font.render(f'Score: {self.score}', True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(WINDOW_WIDTH/2, 50))
        self.screen.blit(score_surface, score_rect)
        
        highscore_surface = font.render(f'High Score: {self.highscore}', True, (255, 255, 255))
        highscore_rect = highscore_surface.get_rect(center=(WINDOW_WIDTH/2, 100))
        self.screen.blit(highscore_surface, highscore_rect)
        
        if not self.game_active:
            start_surface = font.render('Press SPACE to start', True, (255, 255, 255))
            start_rect = start_surface.get_rect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
            self.screen.blit(start_surface, start_rect)
    
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        if not self.game_active:
                            self.reset_game()
                            self.game_active = True
                        self.bird_movement = self.jump_height
            
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