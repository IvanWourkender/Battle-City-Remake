import pygame
import random
import sys

pygame.init()
pygame.mixer.init()

# Початкові настройки
WIDTH, HEIGHT = 640, 520
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle City")
clock = pygame.time.Clock()

# Шрифти
font_big = pygame.font.SysFont("Arial", 72, bold=True)
font_small = pygame.font.SysFont("Arial", 32)

# Кольори
YELLOW, RED, WHITE = (255, 255, 0), (255, 0, 0), (255, 255, 255)
BRICK_COLOR, BLACK, GREEN, GRAY = (160, 40, 0), (0, 0, 0), (0, 255, 0), (100, 100, 100)
TILE_SIZE = 40

MAP_ORIGINAL = [
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,0,1,1,0,0,0,1,1,0,1,1,0,0],
    [0,1,1,0,1,1,0,1,0,1,1,0,1,1,0,0],
    [0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0],
    [0,1,1,0,1,1,0,0,0,1,1,0,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,0,1,1,0,1,1,1,0,1,1,0,1,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,1,0,0,0,0,0,0,0,0,0,1,1,0,0],
    [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0], 
    [0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0], 
    [0,0,0,0,0,1,1,9,1,1,0,0,0,0,0,0], 
]
GAME_MAP = [row[:] for row in MAP_ORIGINAL]

def play_music(track, loop=True):
    try:
        pygame.mixer.music.stop()
        pygame.mixer.music.load(track)
        pygame.mixer.music.play(-1 if loop else 0)
    except:
        pass

class Explosion:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.timer = 15
        self.radius = 5

    def update(self):
        self.timer -= 1
        self.radius += 2

    def draw(self, surface):
        if self.timer > 0:
            pygame.draw.circle(surface, (255, 165, 0), (self.x, self.y), self.radius, 2)
            pygame.draw.circle(surface, RED, (self.x, self.y), self.radius // 2)

class Bullet:
    def __init__(self, x, y, direction, color):
        self.rect = pygame.Rect(x, y, 6, 6)
        self.dir = direction
        self.speed = 6
        self.color = color

    def update(self):
        if self.dir == "UP": self.rect.y -= self.speed
        elif self.dir == "DOWN": self.rect.y += self.speed
        elif self.dir == "LEFT": self.rect.x -= self.speed
        elif self.dir == "RIGHT": self.rect.x += self.speed

class Tank:
    def __init__(self, x, y, color, hp, max_hp):
        self.rect = pygame.Rect(x + 4, y + 4, 32, 32)
        self.color = color
        self.dir = "UP"
        self.speed = 2
        self.hp = hp
        self.max_hp = max_hp
        self.bullets = []
        self.shoot_delay = 0

    def move(self, dx, dy, direction):
        self.dir = direction
        old_pos = self.rect.topleft
        self.rect.x += dx
        self.rect.y += dy
        
        # Колізії зі стінами
        for r in range(len(GAME_MAP)):
            for c in range(len(GAME_MAP[0])):
                if GAME_MAP[r][c] != 0:
                    wall = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(wall):
                        self.rect.topleft = old_pos
                        return False
        
        # Межі екрану
        if self.rect.left < 0 or self.rect.right > WIDTH or self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.rect.topleft = old_pos
            return False
        return True

    def shoot(self, color):
        if self.shoot_delay <= 0:
            bx, by = self.rect.centerx - 3, self.rect.centery - 3
            self.bullets.append(Bullet(bx, by, self.dir, color))
            self.shoot_delay = 45 

    def draw(self):
        # корпус
        pygame.draw.rect(screen, self.color, self.rect)
        # дуло
        barrel = pygame.Rect(0, 0, 8, 10)
        if self.dir == "UP": barrel.midbottom = self.rect.midtop
        elif self.dir == "DOWN": barrel.midtop = self.rect.midbottom
        elif self.dir == "LEFT": 
            barrel = pygame.Rect(0, 0, 10, 8)
            barrel.midright = self.rect.midleft
        elif self.dir == "RIGHT": 
            barrel = pygame.Rect(0, 0, 10, 8)
            barrel.midleft = self.rect.midright
        pygame.draw.rect(screen, self.color, barrel)
        
        # HP
        if self.hp > 0:
            bar_w = 32
            curr_w = (self.hp / self.max_hp) * bar_w
            pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 12, bar_w, 4))
            pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 12, curr_w, 4))

def bullet_logic(tank_obj, targets, explosions):
    global game_status
    for b in tank_obj.bullets[:]:
        b.update()
        
        # Вихід за межі екрану
        if not screen.get_rect().colliderect(b.rect):
            tank_obj.bullets.remove(b)
            continue
        
        # Колізія з картою
        bx, by = int(b.rect.centerx // TILE_SIZE), int(b.rect.centery // TILE_SIZE)
        if 0 <= by < len(GAME_MAP) and 0 <= bx < len(GAME_MAP[0]):
            tile = GAME_MAP[by][bx]
            if tile == 1: # Цегла
                GAME_MAP[by][bx] = 0
                explosions.append(Explosion(b.rect.centerx, b.rect.centery))
                if b in tank_obj.bullets: tank_obj.bullets.remove(b)
                continue
            elif tile == 9: # База
                game_status = "LOSE"
                explosions.append(Explosion(b.rect.centerx, b.rect.centery))
                if b in tank_obj.bullets: tank_obj.bullets.remove(b)

        # Колізія з танками
        for t in targets:
            if b.rect.colliderect(t.rect):
                t.hp -= 1
                explosions.append(Explosion(b.rect.centerx, b.rect.centery))
                if b in tank_obj.bullets: tank_obj.bullets.remove(b)
                break

# Об'єкти та стани
player = Tank(440, 440, YELLOW, 4, 4)
enemies = []
explosions = []
game_status = "MENU"

def reset_game():
    global player, enemies, explosions, game_status, GAME_MAP
    GAME_MAP = [row[:] for row in MAP_ORIGINAL]
    player = Tank(440, 440, YELLOW, 4, 4)
    enemies = [Tank(i*130 + 40, 40, RED, 2, 2) for i in range(4)]
    explosions = []
    game_status = "PLAYING"
    play_music("game_music.mp3")

# Головний цикл
while True:
    screen.fill(BLACK)
    events = pygame.event.get()
    
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if game_status == "MENU":
                if event.key == pygame.K_1: reset_game()
                if event.key == pygame.K_2: game_status = "SETTINGS"
            elif game_status == "SETTINGS":
                if event.key == pygame.K_1: 
                    WIDTH, HEIGHT = 640, 520
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                if event.key == pygame.K_2: 
                    WIDTH, HEIGHT = 800, 600
                    screen = pygame.display.set_mode((WIDTH, HEIGHT))
                if event.key == pygame.K_ESCAPE: game_status = "MENU"
            elif game_status in ["WIN", "LOSE"]:
                if event.key == pygame.K_r: 
                    game_status = "MENU"
                    play_music("menu_music.mp3")

    if game_status == "MENU":
        title = font_big.render("BATTLE CITY", True, YELLOW)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 100))
        screen.blit(font_small.render("1. Start Game", True, WHITE), (WIDTH//2 - 100, 250))
        screen.blit(font_small.render("2. Settings", True, WHITE), (WIDTH//2 - 100, 300))

    elif game_status == "SETTINGS":
        screen.blit(font_big.render("SETTINGS", True, GRAY), (WIDTH//2 - 150, 100))
        screen.blit(font_small.render("1. 640x520 (Default)", True, WHITE), (WIDTH//2 - 150, 250))
        screen.blit(font_small.render("2. 800x600 (Large)", True, WHITE), (WIDTH//2 - 150, 300))
        screen.blit(font_small.render("ESC to Return", True, GREEN), (WIDTH//2 - 100, 400))

    elif game_status == "PLAYING":
        # Рух плеєра
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.move(-3, 0, "LEFT")
        elif keys[pygame.K_RIGHT]: player.move(3, 0, "RIGHT")
        elif keys[pygame.K_UP]: player.move(0, -3, "UP")
        elif keys[pygame.K_DOWN]: player.move(0, 3, "DOWN")
        if keys[pygame.K_SPACE]: player.shoot(YELLOW)
        
        if player.shoot_delay > 0: player.shoot_delay -= 1

        # Рісовка карти
        for r, row in enumerate(GAME_MAP):
            for c, tile in enumerate(row):
                rect = (c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile == 1:
                    pygame.draw.rect(screen, BRICK_COLOR, (rect[0]+1, rect[1]+1, TILE_SIZE-2, TILE_SIZE-2))
                elif tile == 9:
                    pygame.draw.rect(screen, GREEN, (rect[0]+2, rect[1]+2, TILE_SIZE-4, TILE_SIZE-4))
                    pygame.draw.rect(screen, WHITE, (rect[0]+12, rect[1]+12, 16, 16))

        # Логіка плеєра
        bullet_logic(player, enemies, explosions)
        player.draw()
        for b in player.bullets: pygame.draw.rect(screen, b.color, b.rect)

        # Логіка ворогів
        for e in enemies[:]:
            if e.hp <= 0:
                enemies.remove(e)
                continue
            
            # Рандомний рух
            dx, dy = 0, 0
            if e.dir == "UP": dy = -e.speed
            elif e.dir == "DOWN": dy = e.speed
            elif e.dir == "LEFT": dx = -e.speed
            elif e.dir == "RIGHT": dx = e.speed
            
            if not e.move(dx, dy, e.dir) or random.randint(0, 40) == 1:
                e.dir = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            
            if random.randint(0, 60) == 1: e.shoot(RED)
            if e.shoot_delay > 0: e.shoot_delay -= 1
            
            bullet_logic(e, [player], explosions)
            e.draw()
            for b in e.bullets: pygame.draw.rect(screen, b.color, b.rect)

        # Вибухи
        for ex in explosions[:]:
            ex.update()
            ex.draw(screen)
            if ex.timer <= 0: explosions.remove(ex)

        # мови кінця гри
        if player.hp <= 0: 
            game_status = "LOSE"
            play_music("lose_music.mp3", False)
        elif not enemies: 
            game_status = "WIN"
            play_music("win_music.mp3", False)

    elif game_status == "WIN":
        txt = font_big.render("YOU WIN!", True, YELLOW)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))
        screen.blit(font_small.render("Press 'R' for Menu", True, WHITE), (WIDTH//2 - 120, HEIGHT//2 + 50))

    elif game_status == "LOSE":
        txt = font_big.render("YOU LOSE", True, RED)
        screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2 - 50))
        screen.blit(font_small.render("Press 'R' for Menu", True, WHITE), (WIDTH//2 - 120, HEIGHT//2 + 50))

    pygame.display.flip()
    clock.tick(60)