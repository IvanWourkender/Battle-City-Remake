import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 640, 520
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Battle City - Finish Screen")
clock = pygame.time.Clock()

# Шрифти
font_big = pygame.font.SysFont("Arial", 72, bold=True)

# Константи
TILE_SIZE = 40
YELLOW, RED, WHITE = (255, 255, 0), (255, 0, 0), (255, 255, 255)
BRICK_COLOR, BLACK, GREEN = (160, 40, 0), (0, 0, 0), (0, 255, 0)

GAME_MAP = [
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
        
        hit = False
        for r in range(len(GAME_MAP)):
            for c in range(len(GAME_MAP[0])):
                if GAME_MAP[r][c] != 0:
                    wall = pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE)
                    if self.rect.colliderect(wall): hit = True
        
        if hit or self.rect.left < 0 or self.rect.right > WIDTH or \
           self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.rect.topleft = old_pos
            return False
        return True

    def shoot(self, color):
        if self.shoot_delay <= 0:
            bx, by = self.rect.centerx - 3, self.rect.centery - 3
            self.bullets.append(Bullet(bx, by, self.dir, color))
            self.shoot_delay = 40 

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.dir == "UP":    pygame.draw.rect(screen, self.color, (self.rect.centerx-4, self.rect.top-10, 8, 10))
        elif self.dir == "DOWN":  pygame.draw.rect(screen, self.color, (self.rect.centerx-4, self.rect.bottom, 8, 10))
        elif self.dir == "LEFT":  pygame.draw.rect(screen, self.color, (self.rect.left-10, self.rect.centery-4, 10, 8))
        elif self.dir == "RIGHT": pygame.draw.rect(screen, self.color, (self.rect.right, self.rect.centery-4, 10, 8))
        if self.hp > 0:
            bar_width = 32
            current_bar = (self.hp / self.max_hp) * bar_width
            pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y-10, bar_width, 5))
            pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y-10, current_bar, 5))

def draw_text(text, color, y_offset=0):
    text_surf = font_big.render(text, True, color)
    text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2 + y_offset))
    screen.blit(text_surf, text_rect)

def bullet_logic(tank_obj, targets):
    global game_status
    for b in tank_obj.bullets[:]:
        b.update()
        if not screen.get_rect().colliderect(b.rect):
            tank_obj.bullets.remove(b)
            continue
        
        bx, by = int(b.rect.centerx // TILE_SIZE), int(b.rect.centery // TILE_SIZE)
        if 0 <= by < len(GAME_MAP) and 0 <= bx < len(GAME_MAP[0]):
            tile = GAME_MAP[by][bx]
            if tile == 1:
                GAME_MAP[by][bx] = 0
                if b in tank_obj.bullets: tank_obj.bullets.remove(b)
                continue
            elif tile == 9:
                game_status = "LOSE"
                if b in tank_obj.bullets: tank_obj.bullets.remove(b)

        for t in targets:
            if b.rect.colliderect(t.rect):
                t.hp -= 1
                if b in tank_obj.bullets: tank_obj.bullets.remove(b)
                break

player = Tank(440, 440, YELLOW, 4, 4)
enemies = [Tank(i*130 + 20, 20, RED, 2, 2) for i in range(5)]
game_status = "PLAYING" # Може бути "PLAYING", "WIN", "LOSE"

while True:
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: pygame.quit(); sys.exit()

    if game_status == "PLAYING":
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: player.move(-3, 0, "LEFT")
        elif keys[pygame.K_RIGHT]: player.move(3, 0, "RIGHT")
        elif keys[pygame.K_UP]: player.move(0, -3, "UP")
        elif keys[pygame.K_DOWN]: player.move(0, 3, "DOWN")
        if keys[pygame.K_SPACE]: player.shoot(YELLOW)
        
        if player.shoot_delay > 0: player.shoot_delay -= 1

        # Малюємо карту
        for r, row in enumerate(GAME_MAP):
            for c, tile in enumerate(row):
                if tile == 1:
                    pygame.draw.rect(screen, BRICK_COLOR, (c*TILE_SIZE+1, r*TILE_SIZE+1, TILE_SIZE-2, TILE_SIZE-2))
                elif tile == 9:
                    pygame.draw.rect(screen, WHITE, (c*TILE_SIZE+2, r*TILE_SIZE+2, TILE_SIZE-4, TILE_SIZE-4))

        bullet_logic(player, enemies)
        player.draw()
        for b in player.bullets: pygame.draw.rect(screen, b.color, b.rect)

        for e in enemies[:]:
            if e.hp <= 0:
                enemies.remove(e)
                continue
            dx, dy = (e.speed if e.dir=="RIGHT" else -e.speed if e.dir=="LEFT" else 0, 
                      e.speed if e.dir=="DOWN" else -e.speed if e.dir=="UP" else 0)
            if not e.move(dx, dy, e.dir) or random.randint(0, 50) == 1:
                e.dir = random.choice(["UP", "DOWN", "LEFT", "RIGHT", "DOWN"])
            if random.randint(0, 60) == 1: e.shoot(RED)
            if e.shoot_delay > 0: e.shoot_delay -= 1
            bullet_logic(e, [player])
            e.draw()
            for b in e.bullets: pygame.draw.rect(screen, b.color, b.rect)

        if player.hp <= 0: game_status = "LOSE"
        if not enemies: game_status = "WIN"

    # Екран фіналу
    elif game_status == "WIN":
        draw_text("YOU WIN", YELLOW)
    elif game_status == "LOSE":
        draw_text("YOU LOSE", RED)

    pygame.display.flip()
    clock.tick(60)