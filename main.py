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

# Difficulty progression settings
DIFFICULTY_INCREASE_INTERVAL = 5000  # Increase difficulty every 5 seconds (in milliseconds)
MAX_ASTEROID_SPEED = 8
MAX_SPAWN_RATE = 0.08

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
    def __init__(self, x, y, speed=None):
        self.x = x
        self.y = y
        self.width = ASTEROID_WIDTH
        self.height = ASTEROID_HEIGHT
        self.speed = speed if speed is not None else ASTEROID_SPEED
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
        self.score = 10  # Start with 10 points to allow some shooting
        self.lives = 3
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 48)
        
        # High scores
        self.high_score, self.high_level = self.load_high_scores()
        
        # Difficulty progression
        self.game_start_time = pygame.time.get_ticks()
        self.current_asteroid_speed = ASTEROID_SPEED
        self.current_spawn_rate = ASTEROID_SPAWN_RATE
        self.difficulty_level = 1
        
        # Load background image
        try:
            self.background = pygame.image.load(os.path.join("res", "bg.png"))
            self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.background = None
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Shoot bullet (costs 1 point)
                    if self.score > 0:
                        bullet_x = self.player.x + self.player.width // 2 - BULLET_WIDTH // 2
                        bullet_y = self.player.y
                        self.bullets.append(Bullet(bullet_x, bullet_y))
                        self.score -= 1
                        if self.score <= 0:
                            self.game_over = True
                            self.check_and_save_high_scores()
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.restart_game()
    
    def update(self):
        if not self.game_over:
            # Update difficulty
            self.update_difficulty()
            
            # Handle player movement
            keys = pygame.key.get_pressed()
            self.player.move(keys)
            
            # Update bullets
            for bullet in self.bullets[:]:
                bullet.move()
                if bullet.is_off_screen():
                    self.bullets.remove(bullet)
            
            # Spawn asteroids
            if random.random() < self.current_spawn_rate:
                asteroid_x = random.randint(0, SCREEN_WIDTH - ASTEROID_WIDTH)
                self.asteroids.append(Asteroid(asteroid_x, -ASTEROID_HEIGHT, self.current_asteroid_speed))
            
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
                        self.score += 2  # Add 1 points for each asteroid destroyed
                    break
        
        # Check player-asteroid collisions
        for asteroid in self.asteroids[:]:
            if self.player.rect.colliderect(asteroid.rect):
                self.lives -= 1
                self.asteroids.remove(asteroid)
                if self.lives <= 0:
                    self.game_over = True
                    self.check_and_save_high_scores()
    
    def draw(self):
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)
        
        # Draw game objects
        self.player.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Draw score, lives, and difficulty
        self.draw_score()
        self.draw_lives()
        self.draw_difficulty()
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
        
        pygame.display.flip()
    
    def load_high_scores(self):
        try:
            with open("highscores.txt", "r") as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    high_score = int(lines[0].strip())
                    high_level = int(lines[1].strip())
                    print(f"Loaded high scores: Score={high_score}, Level={high_level}")
                    return high_score, high_level
                else:
                    print("Not enough lines in highscores.txt, using defaults")
                    return 0, 1
        except FileNotFoundError:
            print("highscores.txt not found, using defaults")
            return 0, 1
        except Exception as e:
            print(f"Error loading high scores: {e}")
            return 0, 1
    
    def save_high_scores(self, score, level):
        try:
            with open("highscores.txt", "w") as file:
                file.write(f"{score}\n{level}")
            print(f"Saved high scores: Score={score}, Level={level}")
        except Exception as e:
            print(f"Error saving high scores: {e}")
            pass  # Silently fail if can't save
    
    def check_and_save_high_scores(self):
        print(f"Checking high scores - Current: Score={self.score}, Level={self.difficulty_level}")
        print(f"Current highs - Score={self.high_score}, Level={self.high_level}")
        
        # Check if current score is higher than high score
        if self.score > self.high_score:
            print(f"New high score! {self.score} > {self.high_score}")
            self.high_score = self.score
            self.save_high_scores(self.score, self.difficulty_level)
        elif self.score == self.high_score and self.difficulty_level > self.high_level:
            print(f"Same score but higher level! Level {self.difficulty_level} > {self.high_level}")
            self.high_level = self.difficulty_level
            self.save_high_scores(self.score, self.difficulty_level)
        elif self.difficulty_level > self.high_level:
            print(f"Higher level reached! Level {self.difficulty_level} > {self.high_level}")
            self.high_level = self.difficulty_level
            self.save_high_scores(self.high_score, self.difficulty_level)
        else:
            print("No new records")
    
    def draw_high_scores(self):
        # Draw current score and level
        current_score_text = self.small_font.render(f"Final Score: {self.score}", True, WHITE)
        current_level_text = self.small_font.render(f"Level Reached: {self.difficulty_level}", True, WHITE)
        
        current_score_rect = current_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        current_level_rect = current_level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 130))
        
        self.screen.blit(current_score_text, current_score_rect)
        self.screen.blit(current_level_text, current_level_rect)
        
        # Draw high scores
        high_score_text = self.small_font.render(f"High Score: {self.high_score}", True, GREEN)
        high_level_text = self.small_font.render(f"Highest Level: {self.high_level}", True, GREEN)
        
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 160))
        high_level_rect = high_level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 190))
        
        self.screen.blit(high_score_text, high_score_rect)
        self.screen.blit(high_level_text, high_level_rect)
    
    def update_difficulty(self):
        current_time = pygame.time.get_ticks()
        time_elapsed = current_time - self.game_start_time
        
        # Increase difficulty every 5 seconds
        new_level = (time_elapsed // DIFFICULTY_INCREASE_INTERVAL) + 1
        
        if new_level > self.difficulty_level:
            self.difficulty_level = new_level
            
            # Increase asteroid speed (capped at MAX_ASTEROID_SPEED)
            speed_increase = min(0.5, (MAX_ASTEROID_SPEED - self.current_asteroid_speed) / 10)
            self.current_asteroid_speed = min(MAX_ASTEROID_SPEED, self.current_asteroid_speed + speed_increase)
            
            # Increase spawn rate (capped at MAX_SPAWN_RATE)
            spawn_increase = min(0.005, (MAX_SPAWN_RATE - self.current_spawn_rate) / 10)
            self.current_spawn_rate = min(MAX_SPAWN_RATE, self.current_spawn_rate + spawn_increase)
    
    def draw_score(self):
        score_text = self.score_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
    
    def draw_lives(self):
        lives_text = self.score_font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (10, 50))
    
    def draw_difficulty(self):
        difficulty_text = self.score_font.render(f"Level: {self.difficulty_level}", True, WHITE)
        self.screen.blit(difficulty_text, (10, 90))
    
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
        
        # Draw high scores
        self.draw_high_scores()
    
    def restart_game(self):
        # Reset game state
        self.game_over = False
        self.score = 2  # Start with 10 points to allow some shooting
        self.lives = 3
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, 
                           SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.bullets = []
        self.asteroids = []
        
        # Reset difficulty
        self.game_start_time = pygame.time.get_ticks()
        self.current_asteroid_speed = ASTEROID_SPEED
        self.current_spawn_rate = ASTEROID_SPAWN_RATE
        self.difficulty_level = 1
        
        # Reload high scores
        self.high_score, self.high_level = self.load_high_scores()
    
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