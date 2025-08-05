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
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)

# Explosion settings
EXPLOSION_DURATION = 30  # Frames the explosion lasts (0.5 seconds at 60 FPS)
EXPLOSION_SIZE = 60

# Game states
MENU_STATE = "menu"
INSTRUCTIONS_STATE = "instructions"
GAME_STATE = "game"

# Player settings
PLAYER_SPEED = 5
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 50
MAX_PLAYER_WIDTH = 80
MAX_PLAYER_HEIGHT = 80
PLAYER_SIZE_INCREASE = 5  # Increase size by 5 pixels per level

# Bullet settings
BULLET_SPEED = 7
BULLET_WIDTH = 5
BULLET_HEIGHT = 15

# Asteroid settings
ASTEROID_SPEED = 3
ASTEROID_WIDTH = 40
ASTEROID_HEIGHT = 40
ASTEROID_SPAWN_RATE = 0.02  # Probability per frame

# Powerup settings
POWERUP_SPEED = 2
POWERUP_WIDTH = 30
POWERUP_HEIGHT = 30
POWERUP_POINTS = 10

# Difficulty progression settings
POINTS_PER_LEVEL = 10  # Points needed to increase level
MAX_ASTEROID_SPEED = 8
MAX_SPAWN_RATE = 0.08

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.Font(None, 36)
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2)
        
        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.color
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = EXPLOSION_SIZE
        self.height = EXPLOSION_SIZE
        self.duration = EXPLOSION_DURATION
        self.current_frame = 0
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Load explosion image
        try:
            self.image = pygame.image.load(os.path.join("res", "explosion.png"))
            self.image = pygame.transform.scale(self.image, (self.width, self.height))
        except:
            self.image = None
    
    def update(self):
        self.current_frame += 1
        return self.current_frame < self.duration
    
    def draw(self, screen):
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            # Fallback: draw a yellow circle
            pygame.draw.circle(screen, YELLOW, (self.x + self.width // 2, self.y + self.height // 2), self.width // 2)

class Powerup:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = POWERUP_WIDTH
        self.height = POWERUP_HEIGHT
        self.speed = POWERUP_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Load powerup image
        try:
            self.image = pygame.image.load(os.path.join("res", "powerup1.png"))
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
            # Fallback: draw a green diamond
            pygame.draw.polygon(screen, GREEN, [
                (self.x + self.width // 2, self.y),
                (self.x + self.width, self.y + self.height // 2),
                (self.x + self.width // 2, self.y + self.height),
                (self.x, self.y + self.height // 2)
            ])
    
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT

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
            self.original_image = pygame.image.load(os.path.join("res", "SpaceShip.png"))
            self.image = pygame.transform.scale(self.original_image, (self.width, self.height))
        except:
            self.original_image = None
            self.image = None
    
    def resize(self, new_width, new_height):
        self.width = new_width
        self.height = new_height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Resize image if available
        if self.original_image:
            self.image = pygame.transform.scale(self.original_image, (self.width, self.height))
    
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
        self.cost_paid = False  # Track if the shooting cost has been paid
    
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
        self.fps_counter = 0
        
        # Game state
        self.current_state = MENU_STATE
        
        # Menu buttons
        button_width = 200
        button_height = 50
        button_x = SCREEN_WIDTH // 2 - button_width // 2
        
        self.start_button = Button(button_x, 250, button_width, button_height, "Start Game", GREEN, LIGHT_GRAY)
        self.instructions_button = Button(button_x, 320, button_width, button_height, "Instructions", BLUE, LIGHT_GRAY)
        self.quit_button = Button(button_x, 390, button_width, button_height, "Quit", RED, LIGHT_GRAY)
        self.back_button = Button(50, 50, 100, 40, "Back", GRAY, LIGHT_GRAY)
        self.menu_button = Button(button_x, 320, button_width, button_height, "Main Menu", BLUE, LIGHT_GRAY)
        
        # Instructions scrolling
        self.instructions_scroll_y = 0
        self.instructions_scroll_speed = 30
        
        # Game objects
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, 
                           SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.bullets = []
        self.asteroids = []
        self.explosions = []
        self.powerups = []
        
        # Game state
        self.running = True
        self.game_over = False
        self.paused = False
        self.score = 10  # Start with 10 points to allow some shooting
        self.lives = 3
        self.game_over_explosion = None
        self.font = pygame.font.Font(None, 74)
        self.small_font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 48)
        
        # High scores
        self.high_score, self.high_level = self.load_high_scores()
        
        # Difficulty progression
        self.current_asteroid_speed = ASTEROID_SPEED
        self.current_spawn_rate = ASTEROID_SPAWN_RATE
        self.difficulty_level = 1
        self.points_for_next_level = POINTS_PER_LEVEL
        
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
            
            if self.current_state == MENU_STATE:
                self.handle_menu_events(event)
            elif self.current_state == INSTRUCTIONS_STATE:
                self.handle_instructions_events(event)
            elif self.current_state == GAME_STATE:
                self.handle_game_events(event)
    
    def handle_menu_events(self, event):
        if self.start_button.handle_event(event):
            self.start_game()
        elif self.instructions_button.handle_event(event):
            self.current_state = INSTRUCTIONS_STATE
        elif self.quit_button.handle_event(event):
            self.running = False
    
    def handle_instructions_events(self, event):
        if self.back_button.handle_event(event):
            self.current_state = MENU_STATE
            self.instructions_scroll_y = 0  # Reset scroll when leaving
        
        # Handle scrolling with mouse wheel
        if event.type == pygame.MOUSEWHEEL:
            self.instructions_scroll_y -= event.y * self.instructions_scroll_speed
            # Prevent scrolling too far up
            self.instructions_scroll_y = max(self.instructions_scroll_y, -400)
            # Prevent scrolling too far down
            self.instructions_scroll_y = min(self.instructions_scroll_y, 0)
        
        # Handle keyboard scrolling
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.instructions_scroll_y += self.instructions_scroll_speed
                self.instructions_scroll_y = min(self.instructions_scroll_y, 0)
            elif event.key == pygame.K_DOWN:
                self.instructions_scroll_y -= self.instructions_scroll_speed
                self.instructions_scroll_y = max(self.instructions_scroll_y, -400)
    
    def handle_game_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and not self.game_over:
                # Toggle pause
                self.paused = not self.paused
            elif event.key == pygame.K_SPACE and not self.game_over and not self.paused:
                # Shoot bullet (costs 1 point only if it doesn't hit)
                if self.score > 0:
                    bullet_x = self.player.x + self.player.width // 2 - BULLET_WIDTH // 2
                    bullet_y = self.player.y
                    new_bullet = Bullet(bullet_x, bullet_y)
                    new_bullet.cost_paid = False  # Track if we've already paid for this bullet
                    self.bullets.append(new_bullet)
                    self.score -= 1
                    if self.score <= 0:
                        self.game_over = True
                        self.check_and_save_high_scores()
            elif event.key == pygame.K_r and self.game_over:
                # Restart game
                self.restart_game()
        elif event.type == pygame.MOUSEBUTTONDOWN and self.paused:
            # Handle pause screen button clicks
            if self.menu_button.rect.collidepoint(event.pos):
                self.return_to_menu()
    
    def start_game(self):
        self.current_state = GAME_STATE
        self.restart_game()
    
    def return_to_menu(self):
        self.current_state = MENU_STATE
        self.paused = False
        self.restart_game()
    
    def update(self):
        if self.current_state == GAME_STATE and not self.game_over and not self.paused:
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
            
            # Update powerups
            for powerup in self.powerups[:]:
                powerup.move()
                if powerup.is_off_screen():
                    self.powerups.remove(powerup)
            
            # Update explosions
            for explosion in self.explosions[:]:
                if not explosion.update():
                    self.explosions.remove(explosion)
            
            # Collision detection
            self.check_collisions()
    
    def check_collisions(self):
        # Check bullet-asteroid collisions
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if bullet.rect.colliderect(asteroid.rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                        # Refund the bullet cost if it hit an asteroid
                        if not bullet.cost_paid:
                            self.score += 1
                            bullet.cost_paid = True
                    if asteroid in self.asteroids:
                        # Create explosion at asteroid position
                        explosion = Explosion(asteroid.x, asteroid.y)
                        self.explosions.append(explosion)
                        self.asteroids.remove(asteroid)
                        self.score += 1  # Add 2 points for each asteroid destroyed
                    break
        
        # Check player-asteroid collisions
        for asteroid in self.asteroids[:]:
            if self.player.rect.colliderect(asteroid.rect):
                self.lives -= 1
                self.asteroids.remove(asteroid)
                if self.lives <= 0:
                    self.game_over = True
                    # Create explosion at player position
                    self.game_over_explosion = Explosion(self.player.x, self.player.y)
                    self.check_and_save_high_scores()
        
        # Check player-powerup collisions
        for powerup in self.powerups[:]:
            if self.player.rect.colliderect(powerup.rect):
                self.score += POWERUP_POINTS
                self.powerups.remove(powerup)
    
    def draw(self):
        # Draw background
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(BLACK)
        
        if self.current_state == MENU_STATE:
            self.draw_menu()
        elif self.current_state == INSTRUCTIONS_STATE:
            self.draw_instructions()
        elif self.current_state == GAME_STATE:
            self.draw_game()
        
        pygame.display.flip()
    
    def draw_menu(self):
        # Draw title
        title_text = self.font.render("ASTEROID SHOOTER", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Draw buttons
        self.start_button.draw(self.screen)
        self.instructions_button.draw(self.screen)
        self.quit_button.draw(self.screen)
    
    def draw_instructions(self):
        # Draw title
        title_text = self.font.render("INSTRUCTIONS", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw back button
        self.back_button.draw(self.screen)
        
        # Draw scroll instructions
        scroll_text = self.small_font.render("Use mouse wheel or UP/DOWN arrows to scroll", True, GRAY)
        scroll_rect = scroll_text.get_rect(center=(SCREEN_WIDTH // 2, 140))
        self.screen.blit(scroll_text, scroll_rect)
        
        # Instructions text
        instructions = [
            "CONTROLS:",
            "A/D or Arrow Keys - Move ship left/right",
            "Spacebar - Shoot bullet (costs 1 point)",
            "ESC - Pause/Resume game",
            "R - Restart game (when game over)",
            "",
            "GAMEPLAY:",
            "• Destroy asteroids to earn points",
            "• Each asteroid destroyed = +2 points",
            "• Bullet cost is refunded if you hit an asteroid",
            "• Every 10 points = Level up!",
            "",
            "LEVEL PROGRESSION:",
            "• Ship gets bigger each level",
            "• Asteroids move faster",
            "• More asteroids spawn",
            "• Maximum ship size: 80x80 pixels",
            "",
            "OBJECTIVE:",
            "Survive as long as possible and",
            "reach the highest level!",
            "",
            "TIPS:",
            "• Start with small movements to get used to controls",
            "• Save your shots for when you're sure you'll hit",
            "• The bigger your ship gets, the easier it is to hit asteroids",
            "• Don't panic when asteroids get faster - focus on accuracy",
            "• Try to reach higher levels for better high scores!",
            "• Accurate shots are rewarded - missed shots cost points"
        ]
        
        y_offset = 180 + self.instructions_scroll_y
        for line in instructions:
            # Only draw text that's visible on screen
            if y_offset > -30 and y_offset < SCREEN_HEIGHT + 30:
                if line.startswith("•"):
                    color = GREEN
                elif line in ["CONTROLS:", "GAMEPLAY:", "LEVEL PROGRESSION:", "OBJECTIVE:", "TIPS:"]:
                    color = YELLOW
                else:
                    color = WHITE
                
                text_surface = self.small_font.render(line, True, color)
                text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
                self.screen.blit(text_surface, text_rect)
            y_offset += 30
    
    def draw_game(self):
        # Draw game objects
        if self.game_over and self.game_over_explosion:
            # Draw explosion instead of player when game over
            self.game_over_explosion.draw(self.screen)
        else:
            self.player.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(self.screen)
        
        # Draw score, lives, and difficulty
        self.draw_score()
        self.draw_lives()
        self.draw_difficulty()
        
        # Draw pause screen
        if self.paused:
            self.draw_pause_screen()
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
    
    def draw_pause_screen(self):
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw "PAUSED" text
        pause_text = self.font.render("PAUSED", True, YELLOW)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(pause_text, text_rect)
        
        # Draw pause instruction
        pause_instruction = self.small_font.render("Press ESC to resume", True, WHITE)
        instruction_rect = pause_instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(pause_instruction, instruction_rect)
        
        # Draw menu button
        self.menu_button.draw(self.screen)
    
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
        # Increase difficulty based on points
        if self.score >= self.points_for_next_level:
            self.difficulty_level += 1
            
            # Increase asteroid speed (capped at MAX_ASTEROID_SPEED)
            speed_increase = min(0.5, (MAX_ASTEROID_SPEED - self.current_asteroid_speed) / 10)
            self.current_asteroid_speed = min(MAX_ASTEROID_SPEED, self.current_asteroid_speed + speed_increase)
            
            # Increase spawn rate (capped at MAX_SPAWN_RATE)
            spawn_increase = min(0.005, (MAX_SPAWN_RATE - self.current_spawn_rate) / 10)
            self.current_spawn_rate = min(MAX_SPAWN_RATE, self.current_spawn_rate + spawn_increase)
            
            # Increase ship size (capped at MAX_PLAYER_WIDTH/HEIGHT)
            new_width = min(MAX_PLAYER_WIDTH, PLAYER_WIDTH + (self.difficulty_level - 1) * PLAYER_SIZE_INCREASE)
            new_height = min(MAX_PLAYER_HEIGHT, PLAYER_HEIGHT + (self.difficulty_level - 1) * PLAYER_SIZE_INCREASE)
            self.player.resize(new_width, new_height)
            
            # Update points needed for next level
            self.points_for_next_level += POINTS_PER_LEVEL
            
            # Spawn powerup after level up
            powerup_x = random.randint(0, SCREEN_WIDTH - POWERUP_WIDTH)
            self.powerups.append(Powerup(powerup_x, -POWERUP_HEIGHT))
    
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
        self.paused = False
        self.score = 2  # Start with 10 points to allow some shooting
        self.lives = 3
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, 
                           SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.bullets = []
        self.asteroids = []
        self.explosions = []
        self.powerups = []
        self.game_over_explosion = None
        
        # Reset difficulty
        self.current_asteroid_speed = ASTEROID_SPEED
        self.current_spawn_rate = ASTEROID_SPAWN_RATE
        self.difficulty_level = 1
        self.points_for_next_level = POINTS_PER_LEVEL
        
        # Reload high scores
        self.high_score, self.high_level = self.load_high_scores()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            
            # Update FPS counter and window title
            self.fps_counter = int(self.clock.get_fps())
            pygame.display.set_caption(f"Asteroid Shooter - FPS: {self.fps_counter}")
            
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 