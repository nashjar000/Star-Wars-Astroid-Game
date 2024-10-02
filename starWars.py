import pygame
import sys
import random
import os

# Initialize Pygame and its modules
pygame.init()
pygame.mixer.init()

# ------------------------------
# Configuration and Constants
# ------------------------------
# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Star Wars Asteroid Game')

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Frames per second
FPS = 60
CLOCK = pygame.time.Clock()

# Asset paths
ASSETS_DIR = 'assets'  # Ensure you have an 'assets' directory with required images and sounds
SPACESHIP_IMAGE = os.path.join(ASSETS_DIR, 'millennium_falcon.png')
ASTEROID_IMAGE = os.path.join(ASSETS_DIR, 'asteroid.png')
LASER_SOUND_PATH = os.path.join(ASSETS_DIR, 'x-wing_fire.mp3')
EXPLOSION_SOUND_PATH = os.path.join(ASSETS_DIR, 'TIE_fighter_explode.mp3')
BACKGROUND_MUSIC_PATH = os.path.join(ASSETS_DIR, 'StarWarsAstroidField.mp3')
FONT_NAME = None  # Default font
HIGH_SCORE_FILE = 'high_score.txt'

# ------------------------------
# Asset Manager
# ------------------------------
class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}

    def load_image(self, name, path, size=None):
        if not os.path.isfile(path):
            print(f"Error: Image file '{path}' not found.")
            sys.exit(1)
        try:
            image = pygame.image.load(path).convert_alpha()
            if size:
                image = pygame.transform.scale(image, size)
            self.images[name] = image
            return image
        except pygame.error as e:
            print(f"Unable to load image {path}: {e}")
            sys.exit()

    def load_sound(self, name, path):
        if not os.path.isfile(path):
            print(f"Error: Sound file '{path}' not found.")
            sys.exit(1)
        try:
            sound = pygame.mixer.Sound(path)
            self.sounds[name] = sound
            return sound
        except pygame.error as e:
            print(f"Unable to load sound {path}: {e}")
            sys.exit()

    def get_image(self, name):
        return self.images.get(name)

    def get_sound(self, name):
        return self.sounds.get(name)

    def load_font(self, name, path, size):
        try:
            font = pygame.font.Font(path, size)
            self.fonts[name] = font
            return font
        except pygame.error as e:
            print(f"Unable to load font {path}: {e}")
            sys.exit()

    def get_font(self, name):
        return self.fonts.get(name)

# Initialize Asset Manager and load assets
assets = AssetManager()
# Load images
spaceship_img = assets.load_image('spaceship', SPACESHIP_IMAGE, (50, 50))
asteroid_img = assets.load_image('asteroid', ASTEROID_IMAGE, (40, 40))
# Load sounds
laser_sound = assets.load_sound('laser', LASER_SOUND_PATH)
explosion_sound = assets.load_sound('explosion', EXPLOSION_SOUND_PATH)
# Load background music
try:
    pygame.mixer.music.load(BACKGROUND_MUSIC_PATH)
    pygame.mixer.music.set_volume(0.5)
except pygame.error as e:
    print(f"Unable to load background music {BACKGROUND_MUSIC_PATH}: {e}")
    sys.exit()
# Load fonts
font_small = assets.load_font('small', FONT_NAME, 24)
font_medium = assets.load_font('medium', FONT_NAME, 36)
font_large = assets.load_font('large', FONT_NAME, 72)

# Start playing background music
pygame.mixer.music.play(-1)  # Loop indefinitely

# ------------------------------
# Sprite Classes
# ------------------------------
class Spaceship(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__()
        self.original_image = image
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=pos)
        self.speed = 5
        self.lives = 3
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, keys_pressed, *args, **kwargs):
        if keys_pressed[pygame.K_UP]:
            self.rect.y -= self.speed
            if self.rect.top < 0:
                self.rect.top = 0
        if keys_pressed[pygame.K_DOWN]:
            self.rect.y += self.speed
            if self.rect.bottom > SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT
        if keys_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speed
            if self.rect.left < 0:
                self.rect.left = 0
        if keys_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speed
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

class Asteroid(pygame.sprite.Sprite):
    def __init__(self, image, pos, speed):
        super().__init__()
        self.original_image = image
        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(topleft=pos)
        self.speed = speed
        self.rotation = 0
        self.rotation_speed = random.randint(-5, 5)
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args, **kwargs):
        self.rect.x += self.speed
        self.rotate()

        # Remove asteroid if it moves off screen
        if self.rect.left > SCREEN_WIDTH:
            self.kill()

    def rotate(self):
        """Rotate the asteroid for visual effect."""
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.mask = pygame.mask.from_surface(self.image)

class Laser(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((10, 4))
        self.image.fill((255, 0, 0))  # Red laser
        self.rect = self.image.get_rect(center=pos)
        self.speed = -10
        self.mask = pygame.mask.from_surface(self.image)

    def update(self, *args, **kwargs):
        self.rect.x += self.speed
        # Remove laser if it moves off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

# ------------------------------
# Game Functions
# ------------------------------
def load_high_score(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return int(f.read())
        except:
            return 0
    else:
        return 0

def save_high_score(file_path, score):
    try:
        with open(file_path, 'w') as f:
            f.write(str(score))
    except:
        print("Failed to save high score.")

def draw_text(surface, text, font, color, pos, center=True):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    if center:
        text_rect.center = pos
    else:
        text_rect.topleft = pos
    surface.blit(text_obj, text_rect)

def show_start_screen():
    start = True
    blink = True
    blink_timer = 0
    blink_interval = 500  # milliseconds

    while start:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    start = False

        # Handle blinking text
        current_time = pygame.time.get_ticks()
        if current_time - blink_timer >= blink_interval:
            blink = not blink
            blink_timer = current_time

        # Draw start screen
        SCREEN.fill(BLACK)
        draw_text(SCREEN, 'STAR WARS ASTEROID GAME', font_large, WHITE, (SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        if blink:
            draw_text(SCREEN, 'Press Enter to Start', font_medium, WHITE, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        pygame.display.flip()

def show_game_over_screen(score, high_score):
    over = True
    while over:
        CLOCK.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    over = False

        # Draw game over screen
        SCREEN.fill(BLACK)
        draw_text(SCREEN, 'GAME OVER', font_large, WHITE, (SCREEN_WIDTH/2, SCREEN_HEIGHT/4))
        draw_text(SCREEN, f'Score: {score}', font_medium, WHITE, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 40))
        draw_text(SCREEN, f'High Score: {high_score}', font_medium, WHITE, (SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        draw_text(SCREEN, 'Press Enter to Restart', font_medium, WHITE, (SCREEN_WIDTH/2, SCREEN_HEIGHT*3/4))
        pygame.display.flip()

# ------------------------------
# Main Game Function
# ------------------------------
def main():
    # Load high score
    high_score = load_high_score(HIGH_SCORE_FILE)

    # Show start screen
    show_start_screen()

    # Sprite groups
    all_sprites = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    lasers = pygame.sprite.Group()

    # Create spaceship
    spaceship = Spaceship(spaceship_img, (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
    all_sprites.add(spaceship)

    # Define custom event for spawning asteroids
    ADD_ASTEROID_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(ADD_ASTEROID_EVENT, 1000)  # Spawn every 1 second

    # Game variables
    score = 0
    level = 1
    asteroid_speed = 4
    asteroid_spawn_interval = 1000  # milliseconds

    running = True
    while running:
        CLOCK.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_high_score(HIGH_SCORE_FILE, high_score)
                pygame.quit()
                sys.exit()
            elif event.type == ADD_ASTEROID_EVENT:
                # Spawn a new asteroid
                y_pos = random.randint(0, SCREEN_HEIGHT - asteroid_img.get_height())
                asteroid = Asteroid(asteroid_img, (0, y_pos), asteroid_speed)
                all_sprites.add(asteroid)
                asteroids.add(asteroid)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    # Fire a laser
                    laser = Laser(spaceship.rect.midright)
                    all_sprites.add(laser)
                    lasers.add(laser)
                    laser_sound.play()

        # Get pressed keys
        keys_pressed = pygame.key.get_pressed()

        # Update all sprites, passing keys_pressed
        all_sprites.update(keys_pressed)

        # Check for laser-asteroid collisions
        hits = pygame.sprite.groupcollide(asteroids, lasers, True, True, pygame.sprite.collide_mask)
        for hit in hits:
            explosion_sound.play()
            score += 1
            # Increase difficulty every 10 points
            if score % 10 == 0:
                level += 1
                asteroid_speed += 1
                # Decrease spawn interval but set a minimum limit
                asteroid_spawn_interval = max(250, asteroid_spawn_interval - 100)
                pygame.time.set_timer(ADD_ASTEROID_EVENT, asteroid_spawn_interval)

        # Check for asteroid-spaceship collisions
        hits = pygame.sprite.spritecollide(spaceship, asteroids, True, pygame.sprite.collide_mask)
        if hits:
            explosion_sound.play()
            spaceship.lives -= 1
            if spaceship.lives <= 0:
                # Update high score if necessary
                if score > high_score:
                    high_score = score
                    save_high_score(HIGH_SCORE_FILE, high_score)
                show_game_over_screen(score, high_score)
                # Reset game
                main()

        # Draw everything
        SCREEN.fill(BLACK)

        # Optionally, add a scrolling starfield background here

        all_sprites.draw(SCREEN)

        # Draw HUD (Score, High Score, Level, Lives)
        draw_text(SCREEN, f'Score: {score}', font_small, WHITE, (10, 10), center=False)
        draw_text(SCREEN, f'High Score: {high_score}', font_small, WHITE, (10, 40), center=False)
        draw_text(SCREEN, f'Level: {level}', font_small, WHITE, (10, 70), center=False)
        draw_text(SCREEN, f'Lives: {spaceship.lives}', font_small, WHITE, (10, 100), center=False)

        pygame.display.flip()

# ------------------------------
# Entry Point
# ------------------------------
if __name__ == "__main__":
    main()
