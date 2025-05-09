import pygame
import random
import math
import cv2
import numpy as np

pygame.init()

WIDTH, HEIGHT = 950, 600
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
FPS = 60
HEX_RADIUS = 20
HEX_HEIGHT = HEX_RADIUS * math.sqrt(3)

BALL_IMAGES = [
    pygame.image.load("RED.png"),
    pygame.image.load("GREEN.png"),
    pygame.image.load("BLUE.png"),
    pygame.image.load("YELLOW.png"),
    pygame.image.load("PINK.png"),
    pygame.image.load("ORANGE.png"),
    pygame.image.load("PURPLE.png"),
    pygame.image.load("BOMB.png")
]
SHOOTER_IMAGE = pygame.image.load("CANNON.png")
SHOOTER_IMAGE = pygame.transform.scale(SHOOTER_IMAGE, (60, 60))
BALL_IMAGES = [pygame.transform.scale(img, (HEX_RADIUS * 2, HEX_RADIUS * 2)) for img in BALL_IMAGES]
BALL_IMAGES[7] = pygame.transform.scale(BALL_IMAGES[7], (HEX_RADIUS * 2 + 25, HEX_RADIUS * 2 + 25))
BACKGROUND_MUSIC = "bgmusic.mp3"  
POP_SOUND = "popcork.ogg" 

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bubble Shooter")
font = pygame.font.SysFont("Times New Roman", 30)
clock = pygame.time.Clock()

start_image = pygame.image.load("1.png")
game_over_image = pygame.image.load("3.png")

START_STATE = 0
LEVEL_SELECT_STATE = 1
PLAY_STATE = 2
GAME_OVER_STATE = 3
current_state = START_STATE
pop_sound = pygame.mixer.Sound(POP_SOUND)
pop_sound.set_volume(1) 

score = 0
div = 0
connected_with_roof = set()
balls = []
valid_positions = set()
colors = {image: 0 for image in BALL_IMAGES}

class Level:
    def __init__(self, number, num_colors, video_path):
        self.number = number
        self.num_colors = num_colors
        self.available_colors = BALL_IMAGES[:num_colors]
        self.video_path = video_path
        self.video_capture = None
    
    def initialize_video(self):
        if self.video_capture is not None:
            self.video_capture.release()
        self.video_capture = cv2.VideoCapture(self.video_path)
    
    def get_video_frame(self):
        if self.video_capture is None:
            self.initialize_video()
            
        ret, frame = self.video_capture.read()
        if not ret:
            self.video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = self.video_capture.read()
            
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        return frame
    
    def cleanup(self):
        if self.video_capture is not None:
            self.video_capture.release()
            self.video_capture = None

class LevelManager:
    def __init__(self):
        self.levels = [
            Level(1, 3, "background1.mp4"),  
            Level(2, 5, "background2.mp4"), 
            Level(3, 7, "background3.mp4") 
        ]
        self.current_level_idx = 0
        self.level_select_image = pygame.image.load("level.png")
        self.level_select_image = pygame.transform.scale(self.level_select_image, (WIDTH, HEIGHT))
    
    @property
    def current_level(self):
        return self.levels[self.current_level_idx]
    
    def select_level(self, level_idx):
        if self.current_level.video_capture is not None:
            self.current_level.cleanup()
            
        if 0 <= level_idx < len(self.levels):
            self.current_level_idx = level_idx
            self.current_level.initialize_video()
            return True
        return False
    
    def cleanup(self):
        for level in self.levels:
            level.cleanup()
    
    def display_level_select(self, screen):
        screen.blit(self.level_select_image, (0, 0))

def display_start_screen():
    screen.fill(WHITE)
    screen.blit(start_image, (0, 0))
    pygame.display.flip()

def play_background_music():
    
    pygame.mixer.music.load(BACKGROUND_MUSIC)
    pygame.mixer.music.play(-1) 
    pygame.mixer.music.set_volume(0.5)

def display_game_over_screen():
    screen.blit(game_over_image, (0, 0))
    
    score_font = pygame.font.SysFont("Times New Roman", 48)
    message_font = pygame.font.SysFont("Times New Roman", 36)

    time_var = pygame.time.get_ticks() / 500  
    
    score_text = score_font.render(f"Final Score: {score}", True, WHITE)
    score_shadow = score_font.render(f"Final Score: {score}", True, (100, 100, 100))
    score_rect = score_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    score_shadow_rect = score_shadow.get_rect(center=(WIDTH//2 + 2, HEIGHT//2 + 2))
    
    screen.blit(score_shadow, score_shadow_rect)
    screen.blit(score_text, score_rect)

    alpha = int(127 + 127 * math.sin(time_var * 2)) 
    message_text = message_font.render("Click to play again", True, SILVER)
    message_text.set_alpha(alpha)
    message_rect = message_text.get_rect(center=(WIDTH//2, HEIGHT * 2//3))
    screen.blit(message_text, message_rect)

    pygame.display.flip()
    
def reset_game():
    global score, balls, connected_with_roof, div, colors
    score = 0
    div = 0
    balls.clear()
    connected_with_roof.clear()
    colors = {image: 0 for image in BALL_IMAGES}

def poping_bubbles(b, s, isbomb):

    if isbomb:
        bomb_radius = 100
        for ball in balls:
            distance_sq = (ball.rect.centerx - b.rect.centerx) ** 2 + (ball.rect.centery - b.rect.centery) ** 2
            if ball not in s and distance_sq <= bomb_radius ** 2:
                s.add(ball)
                pop_sound.play()
        s.add(b)
        return

    for ball in balls:
        if ball.image == b.image and ball not in s and isCollision(b, ball):
            s.add(ball)
            pop_sound.play()
            poping_bubbles(ball, s, isbomb)
    return

def check(s, num, b):
    if(num >= 3):
        return True
    
    s.add(b)
    ans = False

    for ball in balls:
        if ball not in s and ball.image == b.image and isCollision(b, ball):
            ans = ans or check(s, num + 1, ball)
            if ans:
                return True
    return ans

def traversal(ball, visited):
    if ball in visited:
        return
    
    visited.add(ball)

    for neighbor in balls:
        if neighbor not in visited and isCollision(ball, neighbor):
            traversal(neighbor, visited)

def removeAir():
    visited = set()
    for ball in connected_with_roof:
        traversal(ball, visited)

    global balls, score, colors

    initial = len(balls)
    # Filter the balls and update the colors dictionary separately
    updated_balls = []
    colors = {image: 0 for image in BALL_IMAGES}
    for ball in balls:
        if ball in visited:
            updated_balls.append(ball)
            colors[ball.image] += 1

    balls = updated_balls

    score += (initial - len(balls))*10


def isCollision(Bubble1, Bubble2):
    distance_sq = (Bubble1.rect.centerx - Bubble2.rect.centerx) ** 2 + \
                  (Bubble1.rect.centery - Bubble2.rect.centery) ** 2
    radius_sum_sq = (Bubble1.radius + Bubble2.radius) ** 2
    return distance_sq <= radius_sum_sq + 50

def snap_to_grid(x, y):
    min_distance = float('inf') 

    for (grid_x, grid_y) in valid_positions:
        distance = math.sqrt((x - grid_x) ** 2 + (y - grid_y) ** 2) 
        if distance < min_distance:
            min_distance = distance
            snapped_position = (grid_x, grid_y)

    return snapped_position

def is_ball_in_last_row(current_bubble, prev):
    LAST_ROW_Y = HEIGHT - 100
    for ball in balls:
        if ball.rect.centery >= LAST_ROW_Y and ball != current_bubble and not ball.moving:
            return True
    return False

class Bubble:
    def __init__(self, image, x = WIDTH // 2, y = HEIGHT - 35):
        if len(balls) > 0:
            available_colors = []
            for color_img in BALL_IMAGES: 
                available_colors.append(color_img)
                self.image = image
        else:
            self.image = image
            	
        self.rect = self.image.get_rect(center=(x, y))
        self.radius = HEX_RADIUS
        self.velocity = [15, 15]
        self.moving = False
        self.direction = 0
        self.bomb = False

    def move(self):
        if not self.moving:
            return

        self.rect.x += math.cos(self.direction) * self.velocity[0]
        self.rect.y += math.sin(self.direction) * self.velocity[1]
        global score

        for ball in balls:
            if self != ball and isCollision(ball, self):
                self.moving = False
                self.rect.center = snap_to_grid(self.rect.centerx, self.rect.centery)
                s = set()
                popable = check(s, 1, self)
                if popable or self.bomb:
                    s2 = set()
                    if self.bomb:
                        poping_bubbles(self, s2, True)
                    else:
                        poping_bubbles(self, s2, False)
                    for ball in s2:
                        colors[ball.image] -= 1
                        balls.remove(ball)
                        if ball in connected_with_roof:
                            connected_with_roof.remove(ball)
                        score += 10
                    removeAir()
                return

        # Bounce off walls
        if self.rect.centerx <= 0 or self.rect.centerx >= WIDTH:
            self.velocity[0] *= -1
        if self.rect.centery <= 0:
            self.moving = False
            self.rect.center = snap_to_grid(self.rect.centerx, self.rect.centery)
            if(self.bomb == False):
                connected_with_roof.add(self)
            else:
                s2 = set()
                poping_bubbles(self, s2, True)
                for ball in s2:
                    balls.remove(ball)
                    if ball in connected_with_roof:
                        connected_with_roof.remove(ball)
                    score += 10
                removeAir()
        if self.rect.centery >= HEIGHT:
            self.velocity[1] *= -1

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

class Bomb(Bubble):
    def __init__(self, x=WIDTH // 2, y=HEIGHT - 35):
        self.image = BALL_IMAGES[7]
        self.rect = self.image.get_rect(center = (x, y)) 
        self.radius = 20  # Bomb radius
        self.bomb = True   # Mark it as a bomb
        self.velocity = [10, 10]
        self.moving = False


class Shooter:
    def __init__(self):
        self.position = [WIDTH // 2, HEIGHT - 35]
        self.direction = 0
        self.image = SHOOTER_IMAGE

    def launch(self, bubble, target_pos):
        target_x, target_y = target_pos
        self.direction = math.atan2(target_y - self.position[1], target_x - self.position[0])
        bubble.moving = True
        angle = math.degrees(-self.direction)
        angle = max(4,min(176,angle))
        self.direction = math.radians(angle) 
        
        bubble.direction = -self.direction

    def draw(self, surface):
        target_x, target_y = pygame.mouse.get_pos()
        self.direction = math.atan2(target_y - self.position[1], target_x - self.position[0])
        angle = math.degrees(-self.direction)
        angle=max(4,min(176,angle))

        rotated_image = pygame.transform.rotate(self.image, angle)
        rotated_rect = rotated_image.get_rect(center=self.position)
        surface.blit(rotated_image, rotated_rect)


def initialize_grid(level):
    global balls, colors, connected_with_roof, valid_positions
    
    balls.clear()
    connected_with_roof.clear()
    colors = {image: 0 for image in BALL_IMAGES}
    
    cols = WIDTH // (2 * HEX_RADIUS)
    rows = HEIGHT // (int(HEX_HEIGHT))

    for row in range(rows):
        for col in range(cols):
            x = col * 2 * HEX_RADIUS + (row % 2) * HEX_RADIUS + HEX_RADIUS
            y = row * HEX_HEIGHT + HEX_RADIUS

            if x <= WIDTH and y <= HEIGHT:
                valid_positions.add((x, y))
                if row <= rows // 2 - 1:
                    bubble_image = random.choice(level.available_colors)
                    bubble = Bubble(bubble_image, x, y)
                    balls.append(bubble)
                    colors[bubble.image] += 1

                if row == 0:
                    connected_with_roof.add(bubble)
                    
def main():
    global score, current_state, div
    game_over = False
    shooter = Shooter()
    level_manager = LevelManager()
    current_bubble = None
    prev = None
    ismoving = False
    score = 0
    
    play_background_music()
    
    game_over = False

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: 
                    game_over = True     
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
    
                if current_state == START_STATE:
                    current_state = LEVEL_SELECT_STATE
                
                elif current_state == LEVEL_SELECT_STATE:
                    level_regions = [
                        pygame.Rect(150, 200, 200, 200), 
                        pygame.Rect(600, 200, 200, 200),
                        pygame.Rect(375, 100, 200, 200)  
                    ]
                    
                    for i, region in enumerate(level_regions):
                        if region.collidepoint(mouse_pos):
                            level_manager.select_level(i)
                            current_state = PLAY_STATE
                            reset_game()
                            initialize_grid(level_manager.current_level)
                            current_bubble = Bubble(random.choice(level_manager.current_level.available_colors))
                            prev = current_bubble
                
                elif current_state == GAME_OVER_STATE:
                    current_state = LEVEL_SELECT_STATE
                
                elif current_state == PLAY_STATE and not ismoving:
                    shooter.launch(current_bubble, mouse_pos)
                    balls.append(current_bubble)
                    prev = current_bubble
            
                    if (score + 1) // 200 > div:
                        div = (score + 1) // 200
                        current_bubble = Bomb()
                    else:
                        available_colors = []
                        for color_img in level_manager.current_level.available_colors:
                            if colors[color_img] > 0: 
                                available_colors.append(color_img)
                
                        current_bubble = Bubble(random.choice(available_colors))
                        colors[current_bubble.image] += 1    

        if current_state == START_STATE:
            display_start_screen()
        
        elif current_state == LEVEL_SELECT_STATE:
            level_manager.display_level_select(screen)
        
        elif current_state == GAME_OVER_STATE:
            display_game_over_screen()
        
        elif current_state == PLAY_STATE:
            frame = level_manager.current_level.get_video_frame()
            frame_surface = pygame.surfarray.make_surface(frame)
            screen.blit(frame_surface, (0, 0))
        
            ismoving = prev.moving if prev else False
            current_bubble.move()
            current_bubble.draw(screen)
            shooter.draw(screen)
            
            for ball in balls:
                ball.move()
                ball.draw(screen)
    
            level_text = font.render(f"Level {level_manager.current_level.number}", True, WHITE)
            colors_text = font.render(f"Colors: {level_manager.current_level.num_colors}", True, WHITE)
            score_text = font.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10,HEIGHT - 35))
            screen.blit(level_text, (10,HEIGHT - 65))
            screen.blit(colors_text, (10,HEIGHT -  95))

            if is_ball_in_last_row(current_bubble, prev):
                current_state = GAME_OVER_STATE
            if len(balls) == 0:
                current_state = GAME_OVER_STATE

        pygame.display.flip()
        clock.tick(FPS)

    pygame.mixer.music.stop()
    pygame.mixer.quit()
    level_manager.cleanup()
    pygame.quit()
    
if __name__ == "__main__":
    main()
