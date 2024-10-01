import pygame
import sys
import random
import pygame.mixer
import os

# Initialize Pygame
pygame.init()

# Set the screen dimensions
screen_width = 640 
screen_height = 480
screen = pygame.display.set_mode((screen_width, screen_height))

# Set the title of the window
pygame.display.set_caption('Star Wars Astroid Game')

# Load the spaceship image
spaceship_image = pygame.image.load('millennium_falcon.png')
spaceship_image = pygame.transform.scale(spaceship_image, (30, 30))

# Load the asteroid image
asteroid_image = pygame.image.load('astroid.png')
asteroid_image = pygame.transform.scale(asteroid_image, (20, 20))

# Define some colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Define the spaceship speed
spaceship_speed = 5

# Define the asteroid speed
asteroid_speed = 2

# Define the initial spaceship position
spaceship_x = screen_width / 2
spaceship_y = screen_height / 2

# Lasers:
class Laser:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 5
        self.color = (255, 0, 0, 255) # red
        self.speed = -10

        # Load and play the laser sound effect
        pygame.mixer.init()
        laser_sound = pygame.mixer.Sound('x-wing_fire.mp3')
        laser_sound.set_volume(0.5)
        laser_sound.play()

    def update(self):
        self.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

lasers = []

# Generate asteroids 
def generate_asteroids():
    asteroids = []
    for i in range(5):
        asteroid_x = random.randint(0, screen_width // 2)
        asteroid_y = random.randint(0, screen_height - 20)
        asteroids.append((asteroid_x, asteroid_y))
    return asteroids

# Music:
pygame.mixer.init()
pygame.mixer.music.set_volume(1)  
sound = pygame.mixer.Sound('StarWarsAstroidField.mp3')
pygame.mixer.music.load('StarWarsAstroidField.mp3')
pygame.mixer.music.play(-1, 1)  # -1 means play indefinitely, 1 means loop

asteroids = generate_asteroids()
explosion_sound = pygame.mixer.Sound('TIE_fighter_explode.mp3')
explosion_sound.set_volume(0.5)  # Adjust the volume as needed

score = 0
font = pygame.font.Font(None, 36)

start_game = True
while start_game:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_KP_ENTER or event.key == pygame.K_RETURN:
                start_game = False

    # Draw the start game screen
    screen.fill(BLACK)
    text = font.render('Press Enter to start', 1, WHITE)
    textpos = text.get_rect(center=(screen_width / 2, screen_height / 2))
    font = pygame.font.Font(None, 36)
    blink = pygame.time.get_ticks() % 1000 < 500
    text = font.render('Press Enter to start', 1, WHITE if blink else BLACK)
    screen.blit(text, textpos)

    # Update the screen
    pygame.display.flip()
    pygame.time.Clock().tick(60) 

# Load the high score from the file
high_score_file = 'high_score.txt'
if os.path.exists(high_score_file):
    with open(high_score_file, 'r') as f:
        high_score = int(f.read())
else:
    high_score = 0

# Main game loop
while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                lasers.append(Laser(spaceship_x + 20, spaceship_y + 15))

    # Get the current key presses
    keys = pygame.key.get_pressed()

    # Move the spaceship
    if keys[pygame.K_UP]:
        spaceship_y -= spaceship_speed
    if keys[pygame.K_DOWN]:
        spaceship_y += spaceship_speed
    if keys[pygame.K_LEFT]:
        spaceship_x -= spaceship_speed
    if keys[pygame.K_RIGHT]:
        spaceship_x += spaceship_speed

    # Move and draw the lasers
    for laser in lasers:
        laser.update()
        laser.draw(screen)

        # Remove lasers that are off the screen
        if laser.x < 0:
            lasers.remove(laser)

    # Move the asteroids
    for i, (asteroid_x, asteroid_y) in enumerate(asteroids):
        asteroid_x += asteroid_speed
        if asteroid_x > screen_width:
            asteroid_x = 0
        asteroids[i] = (asteroid_x, asteroid_y)

    # Check for collisions
    if not asteroids:
        asteroids = generate_asteroids()
        score += 1

    for asteroid_x, asteroid_y in asteroids:
        if (spaceship_x - 15 < asteroid_x < spaceship_x + 15 and
            spaceship_y - 15 < asteroid_y < spaceship_y + 15):
            print(f"Game Over! Your score is {score}. High score: {high_score}")
            pygame.quit()
            sys.exit()

        for laser in lasers:
            if (laser.x + laser.width > asteroid_x and
                laser.x < asteroid_x + 20 and
                laser.y + laser.height > asteroid_y and
                laser.y < asteroid_y + 20):
                asteroids.remove((asteroid_x, asteroid_y))
                lasers.remove(laser)
                explosion_sound.play()
                score += 1
                break

    # Draw everything
    screen.fill(BLACK)
    screen.blit(spaceship_image, (spaceship_x, spaceship_y))
    for asteroid_x, asteroid_y in asteroids:
        screen.blit(asteroid_image, (asteroid_x, asteroid_y))
    for laser in lasers:
        laser.draw(screen)

    # Draw the score and high score
    score_text = font.render(f'Score: {score}', 1, WHITE)
    score_textpos = score_text.get_rect(topright=(screen_width - 10, 10))
    high_score_text = font.render(f'High Score: {high_score}', 1, WHITE)
    high_score_textpos = high_score_text.get_rect(topright=(screen_width - 10, 50))
    screen.blit(score_text, score_textpos)
    screen.blit(high_score_text, high_score_textpos)

    # Update the screen
    pygame.display.flip()
    pygame.time.Clock().tick(60)

    # Save the high score
    if score > high_score:
        with open(high_score_file, 'w') as f:
            f.write(str(score))
        high_score = score

