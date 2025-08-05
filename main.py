import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player settings
PLAYER_SPEED = 5
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50

# Bullet settings
BULLET_SPEED = 7
BULLET_WIDTH = 5
BULLET_HEIGHT = 15

# Asteroid settings
ASTEROID_SPEED = 3
ASTEROID_WIDTH = 40
ASTEROID_HEIGHT = 40
ASTEROID_SPAWN_RATE = 0.02  # Probability per frame

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Load player image
        try:
            self.image = pygame.image.load(os.path.join("res", "SpaceShip.png"))
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except:
            self.image = None
    
    def move(self, keys):
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and self.x > 0:
            self.x -= self.speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        
        self.rect.x = self.x
    
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, GREEN, self.rect)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.speed = BULLET_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def move(self):
        self.y -= self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        pygame.draw.rect(screen, RED, self.rect)
    
    def is_off_screen(self):
        return self.y < -self.height

class Asteroid:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = ASTEROID_WIDTH
        self.height = ASTEROID_HEIGHT
        self.speed = ASTEROID_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Load asteroid image (randomly choose from available asteroid images)
        asteroid_images = ["Asteroid1.png", "Asteroid2.png", "Asteroid3.png", "Asteroid4.png"]
        try:
            asteroid_image = random.choice(asteroid_images)
            self.image = pygame.image.load(os.path.join("res", asteroid_image))
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except:
            self.image = None
    
    def move(self):
        self.y += self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, BLUE, self.rect)
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroid Shooter")
        self.clock = pygame.time.Clock()
        
        # Game objects
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, 
                           SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.bullets = []
        self.asteroids = []
        
        # Game state
        self.running = True
        self.game_over = False
        self.score = 0
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 48)
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Shoot bullet
                    bullet_x = self.player.x + self.player.width // 2 - BULLET_WIDTH // 2
                    bullet_y = self.player.y
                    self.bullets.append(Bullet(bullet_x, bullet_y))
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.restart_game()
    
    def update(self):
        if not self.game_over:
            # Handle player movement
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.move()
                if bullet.is_off_screen():
                    self.bullets.remove(bullet)
            
            # Spawn asteroids
            if random.random() < ASTEROID_SPAWN_RATE:
                asteroid_x = random.randint(0, SCREEN_WIDTH - ASTEROID_WIDTH)
                self.asteroids.append(Asteroid(asteroid_x, -ASTEROID_HEIGHT))
            
            # Update asteroids
            for asteroid in self.asteroids[:]:
                asteroid.move()
                if asteroid.is_off_screen():
                    self.asteroids.remove(asteroid)
            
            # Collision detection
            self.check_collisions()
    
    def check_collisions(self):
        # Check bullet-asteroid collisions
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if bullet.rect.colliderect(asteroid.rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)
                        self.score += 1  # Add 10 points for each asteroid destroyed
                    break
        
        # Check player-asteroid collisions
        for asteroid in self.asteroids[:]:
            if self.player.rect.colliderect(asteroid.rect):
                self.game_over = True
    
    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw game objects
        self.player.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Draw score
        self.draw_score()
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def draw_score(self):
        score_text = self.score_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
    
    def draw_game_over(self):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw "GAME OVER" text
        game_over_text = self.font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over_text, text_rect)
        
        # Draw restart instruction
        restart_text = self.small_font.render("Press 'R' to restart", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
    
    def restart_game(self):
        # Reset game state
        self.game_over = False
        self.score = 0
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, 
                           SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.bullets = []
        self.asteroids = []
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 