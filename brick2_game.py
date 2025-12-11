import pygame
import random

pygame.init()
WIDTH, HEIGHT = 640, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("벽돌깨기 게임")
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
RED = (255, 100, 100)
BLUE = (100, 100, 255)
GREEN = (100, 255, 100)
YELLOW = (255, 255, 100)
BLACK = (0, 0, 0)

class Paddle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_width = 100
        self.max_width = 200
        self.image = pygame.Surface((self.original_width, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 30
        self.speed = 8

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]: self.rect.x += self.speed
        self.rect.clamp_ip(screen.get_rect())

    def extend(self):
        new_width = min(self.rect.width + 30, self.max_width)
        self.image = pygame.Surface((new_width, 15))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=self.rect.center)

class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (6, 6), 6)
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = random.choice([-4, 4])
        self.vy = -4

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy

        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.vx *= -1
        if self.rect.top <= 0:
            self.vy *= -1
        if self.rect.bottom >= HEIGHT:
            self.kill()

class Brick(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((55, 25))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Item(pygame.sprite.Sprite):
    def __init__(self, x, y, kind):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.kind = kind
        if kind == "extend":
            self.image.fill(YELLOW)
        elif kind == "life":
            self.image.fill(GREEN)
        elif kind == "multi":
            self.image.fill(BLUE)
        elif kind == "speedup":
            self.image.fill(RED)
        elif kind == "missile":
            self.image.fill(GRAY)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 15))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -10

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()

STAGES = [
    [[1]*10 for _ in range(5)],
    [[(i+j)%2 for i in range(10)] for j in range(6)],
    [[1 if i%2==0 else 0 for i in range(10)] for _ in range(7)],
    [[random.randint(0,1) for i in range(10)] for _ in range(8)],
    [[1]*10 for _ in range(9)],
    [[(i*j)%3 for i in range(10)] for j in range(10)],
]

all_sprites = pygame.sprite.Group()
bricks = pygame.sprite.Group()
balls = pygame.sprite.Group()
items = pygame.sprite.Group()
missiles = pygame.sprite.Group()

paddle = Paddle()
all_sprites.add(paddle)

lives = 3
stage = 0
score = 0
missile_mode = False
font = pygame.font.SysFont(None, 36)

MARGIN_X = 5
MARGIN_Y = 5


def load_stage(idx):
    bricks.empty()
    for row_idx, row in enumerate(STAGES[idx]):
        for col_idx, val in enumerate(row):
            if val:
                color = random.choice([RED, GREEN, BLUE, GRAY])
                x = col_idx * (55 + MARGIN_X) + 10
                y = row_idx * (25 + MARGIN_Y) + 40
                brick = Brick(x, y, color)
                bricks.add(brick)
                all_sprites.add(brick)
    ball = Ball(WIDTH // 2, HEIGHT // 2)
    balls.add(ball)
    all_sprites.add(ball)

load_stage(stage)

running = True
while running:
    clock.tick(60)
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if missile_mode and keys[pygame.K_SPACE]:
        missile = Missile(paddle.rect.centerx, paddle.rect.top)
        missiles.add(missile)
        all_sprites.add(missile)

    all_sprites.update()

    for ball in balls:
        if ball.rect.colliderect(paddle.rect):
            ball.vy *= -1

        hits = pygame.sprite.spritecollide(ball, bricks, True)
        for hit in hits:
            ball.vy *= -1
            score += 10
            if random.random() < 0.3:
                kind = random.choice(["extend", "life", "multi", "speedup", "missile"])
                item = Item(hit.rect.centerx, hit.rect.centery, kind)
                items.add(item)
                all_sprites.add(item)

    for item in items:
        if item.rect.colliderect(paddle.rect):
            if item.kind == "extend":
                paddle.extend()
            elif item.kind == "life":
                lives += 1
            elif item.kind == "multi":
                if len(balls) < 5:
                    new_ball = Ball(paddle.rect.centerx, paddle.rect.top)
                    balls.add(new_ball)
                    all_sprites.add(new_ball)
            elif item.kind == "speedup":
                for ball in balls:
                    ball.vx *= 1.5
                    ball.vy *= 1.5
            elif item.kind == "missile":
                missile_mode = True
            item.kill()

    for missile in missiles:
        hit = pygame.sprite.spritecollideany(missile, bricks)
        if hit:
            missile.kill()
            hit.kill()
            score += 10

    if len(bricks) == 0:
        stage += 1
        missile_mode = False
        if stage >= len(STAGES):
            print("게임 클리어!")
            running = False
        else:
            load_stage(stage)

    if len(balls) == 0:
        lives -= 1
        missile_mode = False
        if lives <= 0:
            print("게임 오버")
            running = False
        else:
            load_stage(stage)

    all_sprites.draw(screen)
    text = font.render(f"Score: {score}   Lives: {lives}   Stage: {stage+1}", True, WHITE)
    screen.blit(text, (20, HEIGHT - 40))
    pygame.display.flip()

pygame.quit()