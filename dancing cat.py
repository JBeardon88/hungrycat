import os
import pygame
import math
import random

# Change the working directory to the script's directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Current working directory:", os.getcwd())

# Initialize Pygame
pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cat and Mouse Chase")

# Colors
SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)

# Load sounds if available
def load_sound(file_name):
    try:
        return pygame.mixer.Sound(file_name)
    except FileNotFoundError:
        return None

meow_sound = load_sound("meow.wav")
eat_sound = load_sound("eat.wav")

try:
    pygame.mixer.music.load("background.mp3")
    pygame.mixer.music.play(-1)  # Play background music on loop
except FileNotFoundError:
    pass

# Cat properties
cat_x = WIDTH // 2
cat_y = HEIGHT - 100
cat_size = 80
cat_speed = 3
cat_eating = False
eat_timer = 0
EAT_DURATION = 30  # frames
tummy_bar = 50  # Tummy bar starts at half
TUMMY_BAR_MAX = 100
cat_vx = 0
cat_vy = 0
cat_on_ground = True
CAT_JUMP_STRENGTH = -10
GRAVITY = 0.5

# Mouse properties
class Mouse:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.fall_speed = 2
        self.run_speed = 2
        self.grounded = False
        self.direction = 1 if x < WIDTH // 2 else -1
        self.hiding = False

class PowerUp:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30
        self.type = random.choice(["speed", "size", "magnet"])
        self.color = {
            "speed": (255, 0, 0),  # Red
            "size": (0, 255, 0),   # Green
            "magnet": (0, 0, 255)  # Blue
        }[self.type]

class Obstacle:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

# List to store multiple mice
mice = []

# Ground level
GROUND_LEVEL = HEIGHT - 50

# After the mice list, add these new lists:
power_ups = []
obstacles = [
    Obstacle(100, GROUND_LEVEL - 80, 60, 80),
    Obstacle(400, GROUND_LEVEL - 100, 80, 100),
    Obstacle(700, GROUND_LEVEL - 60, 50, 60)
]

# After GROUND_LEVEL = HEIGHT - 50, add these new global variables:
DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]
current_difficulty = 0
game_over = False
power_up_timer = 0
POWER_UP_DURATION = 300  # 5 seconds at 60 FPS

# Animation properties
angle = 0
animation_speed = 0.1

# Score and high score
score = 0
high_score = 0

# Font for scoreboard
font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()

def draw_background():
    # Draw sky and ground
    screen.fill(SKY_BLUE)
    pygame.draw.rect(screen, GREEN, (0, GROUND_LEVEL, WIDTH, HEIGHT - GROUND_LEVEL))  # Ground
    
    # Add some background elements like trees and clouds
    # Trees
    pygame.draw.rect(screen, (139, 69, 19), (100, GROUND_LEVEL - 100, 20, 100))  # Tree trunk
    pygame.draw.circle(screen, (34, 139, 34), (110, GROUND_LEVEL - 120), 40)     # Tree foliage
    pygame.draw.rect(screen, (139, 69, 19), (700, GROUND_LEVEL - 100, 20, 100))  # Tree trunk
    pygame.draw.circle(screen, (34, 139, 34), (710, GROUND_LEVEL - 120), 40)     # Tree foliage
    
    # Clouds
    pygame.draw.circle(screen, WHITE, (200, 100), 30)
    pygame.draw.circle(screen, WHITE, (230, 100), 40)
    pygame.draw.circle(screen, WHITE, (260, 100), 30)
    pygame.draw.circle(screen, WHITE, (600, 150), 30)
    pygame.draw.circle(screen, WHITE, (630, 150), 40)
    pygame.draw.circle(screen, WHITE, (660, 150), 30)

    for obstacle in obstacles:
        pygame.draw.rect(screen, (139, 69, 19), obstacle.rect)  # Brown color for obstacles

def draw_cat(x, y, size, angle, eating):
    body_y = y + math.sin(angle) * 10
    
    # Body (more oval)
    pygame.draw.ellipse(screen, ORANGE, (x - size//2, body_y - size//3, size, size*2//3))
    
    # Head (larger and rounder)
    pygame.draw.circle(screen, ORANGE, (x, body_y - size//3), size//2)
    
    # Eyes (larger and more expressive)
    eye_y = body_y - size//3 - 10
    pygame.draw.circle(screen, WHITE, (x - 15, eye_y), 12)
    pygame.draw.circle(screen, WHITE, (x + 15, eye_y), 12)
    pygame.draw.circle(screen, BLACK, (x - 15, eye_y), 6)
    pygame.draw.circle(screen, BLACK, (x + 15, eye_y), 6)
    
    # Cute pink cheeks
    pygame.draw.circle(screen, PINK, (x - 25, body_y - size//3 + 10), 8)
    pygame.draw.circle(screen, PINK, (x + 25, body_y - size//3 + 10), 8)
    
    # Nose
    pygame.draw.circle(screen, PINK, (x, body_y - size//3 + 10), 5)
    
    # Mouth (changes when eating)
    if eating:
        pygame.draw.circle(screen, BLACK, (x, body_y - size//3 + 25), 15)
        draw_stars(x, body_y - size // 3)
    else:
        pygame.draw.arc(screen, BLACK, (x - 15, body_y - size//3 + 15, 30, 20), 0, math.pi, 2)
    
    # Ears (more triangular and expressive)
    pygame.draw.polygon(screen, ORANGE, [(x - 40, body_y - size//2 - 30), (x - 20, body_y - size//2 + 10), (x - 10, body_y - size//2 - 20)])
    pygame.draw.polygon(screen, ORANGE, [(x + 40, body_y - size//2 - 30), (x + 20, body_y - size//2 + 10), (x + 10, body_y - size//2 - 20)])
    
    # Paws (rounder)
    paw_y = body_y + size//3
    pygame.draw.circle(screen, ORANGE, (x - size//3, paw_y), 15)
    pygame.draw.circle(screen, ORANGE, (x + size//3, paw_y), 15)
    
    # Tail (curvier)
    tail_points = [
        (x + size//2, body_y),
        (x + size//2 + 20, body_y + 20),
        (x + size//2 + 40, body_y + math.sin(angle * 2) * 30)
    ]
    pygame.draw.lines(screen, ORANGE, False, tail_points, 8)

def draw_mouse(mouse):
    x, y, size = mouse.x, mouse.y, mouse.size
    # Body
    pygame.draw.ellipse(screen, GRAY, (x - size//2, y - size//4, size, size//2))
    
    # Head
    pygame.draw.circle(screen, GRAY, (x + size//2 * mouse.direction, y), size//3)
    
    # Ear
    pygame.draw.circle(screen, PINK, (x + (size//2 + 5) * mouse.direction, y - 5), size//6)
    
    # Eye
    pygame.draw.circle(screen, BLACK, (x + (size//2 + 5) * mouse.direction, y), 2)
    
    # Tail
    pygame.draw.line(screen, GRAY, (x - size//2 * mouse.direction, y), (x - size * mouse.direction, y + size//4), 2)

def draw_power_up(power_up):
    pygame.draw.circle(screen, power_up.color, (power_up.x, power_up.y), power_up.size // 2)
    font = pygame.font.Font(None, 20)
    text = font.render(power_up.type[0].upper(), True, WHITE)
    text_rect = text.get_rect(center=(power_up.x, power_up.y))
    screen.blit(text, text_rect)

def handle_power_ups():
    global cat_speed, cat_size, power_up_timer

    if random.random() < 0.005:  # Small chance to spawn a power-up
        x = random.randint(0, WIDTH)
        y = random.randint(0, GROUND_LEVEL - 50)
        power_ups.append(PowerUp(x, y))

    for power_up in power_ups[:]:
        draw_power_up(power_up)
        if abs(cat_x - power_up.x) < cat_size // 2 and abs(cat_y - power_up.y) < cat_size // 2:
            if power_up.type == "speed":
                cat_speed *= 1.5
            elif power_up.type == "size":
                cat_size *= 1.2
            elif power_up.type == "magnet":
                # Implement magnet logic in the main game loop
                pass
            power_up_timer = POWER_UP_DURATION
            power_ups.remove(power_up)

    if power_up_timer > 0:
        power_up_timer -= 1
        if power_up_timer == 0:
            cat_speed = 3  # Reset to default
            cat_size = 80  # Reset to default

def draw_stars(x, y):
    for _ in range(5):
        star_x = x + random.randint(-20, 20)
        star_y = y + random.randint(-20, 20)
        pygame.draw.circle(screen, YELLOW, (star_x, star_y), 5)

def draw_tummy_bar():
    bar_width = 200
    bar_height = 20
    bar_x = WIDTH // 2 - bar_width // 2
    bar_y = 20
    tummy_percentage = tummy_bar / TUMMY_BAR_MAX
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, GREEN, (bar_x, bar_y, bar_width * tummy_percentage, bar_height))

def reset_game():
    global score, mice, cat_x, cat_y, cat_eating, eat_timer, angle, game_over, power_ups, power_up_timer, tummy_bar, cat_vx, cat_vy, cat_on_ground
    score = 0
    mice = []
    cat_x = WIDTH // 2
    cat_y = HEIGHT - 100
    cat_eating = False
    eat_timer = 0
    angle = 0
    game_over = False
    power_ups = []
    power_up_timer = 0
    tummy_bar = 50  # Reset tummy bar to half
    cat_vx = 0
    cat_vy = 0
    cat_on_ground = True

running = True
paused = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key == pygame.K_r:
                reset_game()
            elif event.key == pygame.K_d:
                current_difficulty = (current_difficulty + 1) % len(DIFFICULTY_LEVELS)
            elif event.key in [pygame.K_LEFT, pygame.K_a]:
                cat_vx = -cat_speed
            elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                cat_vx = cat_speed
            elif event.key in [pygame.K_UP, pygame.K_w] and cat_on_ground:
                cat_vy = CAT_JUMP_STRENGTH
                cat_on_ground = False
        elif event.type == pygame.KEYUP:
            if event.key in [pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d]:
                cat_vx = 0
        elif event.type == pygame.MOUSEBUTTONDOWN and not paused and not game_over:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mice.append(Mouse(mouse_x, mouse_y))
            if meow_sound:
                meow_sound.play()

    if paused or game_over:
        # Draw pause or game over menu
        menu_font = pygame.font.Font(None, 48)
        if paused:
            menu_text = menu_font.render("PAUSED", True, BLACK)
        else:
            menu_text = menu_font.render("GAME OVER", True, BLACK)
        screen.blit(menu_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))
        
        restart_text = font.render("Press R to restart", True, BLACK)
        screen.blit(restart_text, (WIDTH // 2 - 100, HEIGHT // 2 + 50))
        
        pygame.display.flip()
        continue

    # Apply gravity
    cat_vy += GRAVITY
    cat_y += cat_vy
    if cat_y >= GROUND_LEVEL - cat_size // 2:
        cat_y = GROUND_LEVEL - cat_size // 2
        cat_vy = 0
        cat_on_ground = True

    # Apply horizontal movement
    cat_x += cat_vx

    # Ensure cat stays within screen bounds
    cat_x = max(0, min(WIDTH, cat_x))

    # Draw background
    draw_background()

    # Handle cat eating animation
    if not cat_eating and mice:
        nearest_mouse = min(mice, key=lambda m: math.hypot(cat_x - m.x, cat_y - m.y))
        if abs(cat_x - nearest_mouse.x) < cat_size//2 and abs(cat_y - nearest_mouse.y) < cat_size//2:
            cat_eating = True
            eat_timer = 0
            mice.remove(nearest_mouse)
            score += 1
            tummy_bar = min(tummy_bar + 10, TUMMY_BAR_MAX)  # Increase tummy bar
            if eat_sound:
                eat_sound.play()
    else:
        eat_timer += 1
        if eat_timer >= EAT_DURATION:
            cat_eating = False
            eat_timer = 0

    # Decrease tummy bar over time
    if not paused and not game_over:
        tummy_bar -= 0.05
        if tummy_bar <= 0:
            game_over = True
        elif tummy_bar >= TUMMY_BAR_MAX:
            game_over = True
            # Cat takes a happy nap
            menu_font = pygame.font.Font(None, 48)
            menu_text = menu_font.render("KITTY TAKES A HAPPY NAP!", True, BLACK)
            screen.blit(menu_text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))
            pygame.display.flip()
            pygame.time.delay(3000)  # Delay to show the message before game over

    # Adjust cat size and speed based on tummy bar
    cat_size = 80 + (tummy_bar - 50) // 5
    cat_speed = 3 - (tummy_bar - 50) // 50

    # Handle power-ups
    handle_power_ups()

    # Apply difficulty settings
    if DIFFICULTY_LEVELS[current_difficulty] == "Easy":
        mouse_spawn_chance = 0.01
        mouse_speed_multiplier = 0.8
    elif DIFFICULTY_LEVELS[current_difficulty] == "Medium":
        mouse_spawn_chance = 0.02
        mouse_speed_multiplier = 1.0
    else:  # Hard
        mouse_spawn_chance = 0.03
        mouse_speed_multiplier = 1.2

    # Randomly spawn mice based on difficulty
    if random.random() < mouse_spawn_chance:
        spawn_x = random.randint(0, WIDTH)
        new_mouse = Mouse(spawn_x, 0)  # Spawn mice at the top of the screen
        new_mouse.run_speed *= mouse_speed_multiplier
        mice.append(new_mouse)

    # Handle mouse movement and collision
    for mouse in mice[:]:
        if not mouse.grounded:
            mouse.y += mouse.fall_speed
            if mouse.y >= GROUND_LEVEL - mouse.size // 2:
                mouse.y = GROUND_LEVEL - mouse.size // 2
                mouse.grounded = True
                if meow_sound:
                    meow_sound.play()
                # Make the mouse run away from the cat after landing
                mouse.direction = 1 if mouse.x < cat_x else -1
        else:
            mouse.x += mouse.run_speed * mouse.direction
            # Randomly change direction
            if random.random() < 0.01:
                mouse.direction *= -1
            
            # Check collision with obstacles
            mouse_rect = pygame.Rect(mouse.x - mouse.size // 2, mouse.y - mouse.size // 2, mouse.size, mouse.size)
            for obstacle in obstacles:
                if mouse_rect.colliderect(obstacle.rect):
                    mouse.direction *= -1  # Reverse direction
                    mouse.hiding = True
                    break
                else:
                    mouse.hiding = False
            
            if not mouse.hiding:
                draw_mouse(mouse)

            # Check for collision with cat's feet
            if not cat_eating and abs(cat_x - mouse.x) < cat_size//3 and abs(cat_y + 40 - mouse.y) < cat_size//3:
                score += 1
                cat_eating = True
                mice.remove(mouse)
                tummy_bar = min(tummy_bar + 10, TUMMY_BAR_MAX)  # Increase tummy bar
                if eat_sound:
                    eat_sound.play()
            elif mouse.x < 0 or mouse.x > WIDTH:
                score -= 1
                mice.remove(mouse)

    # Draw the cat
    draw_cat(cat_x, cat_y, cat_size, angle, cat_eating)

    # Draw the tummy bar
    draw_tummy_bar()

    # Draw scoreboard
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (WIDTH - 120, 20))

    # Update high score
    if score > high_score:
        high_score = score
    high_score_text = font.render(f"High Score: {high_score}", True, BLACK)
    screen.blit(high_score_text, (20, 20))

    # Draw difficulty level
    difficulty_text = font.render(f"Difficulty: {DIFFICULTY_LEVELS[current_difficulty]}", True, BLACK)
    screen.blit(difficulty_text, (20, 60))

    # Check for game over condition
    if score < -10:
        game_over = True

    # Update the display
    pygame.display.flip()

    # Increase the angle for the next frame
    angle += animation_speed

    # Control the frame rate
    clock.tick(60)

pygame.quit()
