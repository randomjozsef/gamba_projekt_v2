import pygame
import time
import math

# Pygame inicializálás
pygame.init()

# Képernyő felbontás lekérése
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h

# Képernyő beállításai
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Cubic Platformer")

# Színek
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

class Player:
    def __init__(self):
        self.width = 10
        self.height = 50
        self.respawn()
        self.speed = 2  # Csökkentett sebesség a kezelhetőbb mozgás érdekében
        self.velocity_y = 0
        self.gravity = 0.1  # Csökkentett gravitáció a lassabb esés érdekében
        self.jump_power = -5  # Megnövelt ugróerő a magasabb ugrások érdekében
        self.on_ground = False
        self.jump_pressed = False  # Inicializálja a jump_pressed értékét False-ra
        self.hook_active = False  # Inicializálja a hook_active értékét False-ra
        self.hook_x = 0
        self.hook_y = 0
        self.swinging = False  # Inicializálja a swinging értékét False-ra

    def respawn(self):
        self.x, self.y = respawn_point
        self.velocity_y = 0
        self.on_ground = False  # Biztosítja, hogy az on_ground értéke visszaálljon

    def move(self, keys, platforms, checkpoints):
        dx = 0
        dy = self.velocity_y

        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        
        if keys[pygame.K_UP] and self.on_ground and not self.jump_pressed:
            self.velocity_y = self.jump_power
            self.on_ground = False
            self.jump_pressed = True  # Állítsa a jump_pressed értékét True-ra ugráskor
        
        if not keys[pygame.K_UP]:
            self.jump_pressed = False  # Állítsa vissza a jump_pressed értékét, amikor az ugrás gombot felengedik
        
        if not self.hook_active:  # Csak akkor alkalmazza a gravitációt, ha a grappling hook nem aktív
            self.velocity_y += self.gravity
            dy = self.velocity_y
        
        self.x += dx
        self.y += dy

        # Ütközés ellenőrzése platformokkal
        self.on_ground = False
        for platform in platforms:
            if pygame.Rect(self.x, self.y + self.height, self.width, 1).colliderect(platform):
                self.y = platform.y - self.height
                self.velocity_y = 0
                self.on_ground = True
            if pygame.Rect(self.x, self.y, self.width, self.height).colliderect(platform):
                if dx > 0:  # Jobbra mozgás; Ütközés a platform bal oldalával
                    self.x = platform.x - self.width
                if dx < 0:  # Balra mozgás; Ütközés a platform jobb oldalával
                    self.x = platform.x + platform.width

        # Ellenőrzés, hogy a karakter elérte-e a checkpointot
        for checkpoint in checkpoints:
            if pygame.Rect(self.x, self.y, self.width, self.height).colliderect(checkpoint):
                return True

        # Ha a karakter leesik a képernyőről, respawnol
        if self.y > SCREEN_HEIGHT:
            self.respawn()

        # Grappling hook mechanika
        if self.hook_active:
            hook_dx = self.hook_x - self.x
            hook_dy = self.hook_y - self.y
            distance = math.sqrt(hook_dx ** 2 + hook_dy ** 2)
            if distance > 5:
                self.x += hook_dx / distance * self.speed * 2  # Növelt sebesség a gyorsabb húzás érdekében
                self.y += hook_dy / distance * self.speed * 2
                self.swinging = True
            else:
                self.hook_active = False
                self.swinging = False
            self.velocity_y = 0  # Megakadályozza az esést, amikor a grappling hook aktív

        # Swing mechanika
        if self.swinging:
            if keys[pygame.K_LEFT]:
                self.x -= self.speed
            if keys[pygame.K_RIGHT]:
                self.x += self.speed

        # Ütközés ellenőrzése falakkal
        if self.x < 0:
            self.x = 0
        if self.x + self.width > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - self.width

        return False

    def draw(self, screen):
        pygame.draw.line(screen, BLUE, (self.x + 5, self.y), (self.x + 5, self.y + 40), 5)  # Test
        pygame.draw.circle(screen, BLUE, (self.x + 5, self.y - 10), 10)  # Fej
        pygame.draw.line(screen, BLUE, (self.x, self.y + 20), (self.x + 10, self.y + 20), 5)  # Karok
        pygame.draw.line(screen, BLUE, (self.x, self.y + 50), (self.x + 10, self.y + 50), 5)  # Lábak
        if self.hook_active:
            pygame.draw.line(screen, WHITE, (self.x + 5, self.y), (self.hook_x, self.hook_y), 1)  # Grappling hook

class Bullet:
    def __init__(self, x, y, direction):
        self.width = 10
        self.height = 10
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 8

    def move(self):
        if self.direction == "left":
            self.x -= self.speed
        elif self.direction == "right":
            self.x += self.speed
        elif self.direction == "up":
            self.y -= self.speed
        elif self.direction == "down":
            self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, WHITE, (self.x, self.y, self.width, self.height))

# Platformok és checkpointok beállítása
maps = [
    {
        "platforms": [
            pygame.Rect(100, 800, 300, 20),
            pygame.Rect(500, 600, 300, 20),
            pygame.Rect(900, 400, 300, 20),
            pygame.Rect(1300, 200, 300, 20),
            pygame.Rect(0, 0, 50, SCREEN_HEIGHT),  # Bal fal
            pygame.Rect(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT)  # Jobb fal
        ],
        "checkpoints": [
            pygame.Rect(1400, 150, 50, 50)  # Checkpoint a következő pályára
        ],
        "respawn": (100, 750)
    },
    {
        "platforms": [
            pygame.Rect(200, 700, 300, 20),
            pygame.Rect(600, 500, 300, 20),
            pygame.Rect(1000, 300, 300, 20),
            pygame.Rect(1400, 100, 300, 20),
            pygame.Rect(0, 0, 50, SCREEN_HEIGHT),  # Bal fal
            pygame.Rect(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT)  # Jobb fal
        ],
        "checkpoints": [
            pygame.Rect(1500, 50, 50, 50)  # Checkpoint a következő pályára
        ],
        "respawn": (200, 650)
    },
    {
        "platforms": [
            pygame.Rect(300, 750, 300, 20),
            pygame.Rect(700, 550, 300, 20),
            pygame.Rect(1100, 350, 300, 20),
            pygame.Rect(1500, 150, 300, 20),
            pygame.Rect(0, 0, 50, SCREEN_HEIGHT),  # Bal fal
            pygame.Rect(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT)  # Jobb fal
        ],
        "checkpoints": [
            pygame.Rect(1600, 100, 50, 50)  # Checkpoint a következő pályára
        ],
        "respawn": (300, 700)
    },
    {
        "platforms": [
            pygame.Rect(400, 800, 200, 20),
            pygame.Rect(800, 600, 200, 20),
            pygame.Rect(1200, 400, 200, 20),
            pygame.Rect(1600, 200, 200, 20),
            pygame.Rect(0, 0, 50, SCREEN_HEIGHT),  # Bal fal
            pygame.Rect(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT)  # Jobb fal
        ],
        "checkpoints": [
            pygame.Rect(1700, 150, 50, 50)  # Checkpoint a következő pályára
        ],
        "respawn": (400, 750)
    },
    {
        "platforms": [
            pygame.Rect(500, 750, 250, 20),
            pygame.Rect(900, 550, 250, 20),
            pygame.Rect(1300, 350, 250, 20),
            pygame.Rect(1700, 150, 250, 20),
            pygame.Rect(0, 0, 50, SCREEN_HEIGHT),  # Bal fal
            pygame.Rect(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT)  # Jobb fal
        ],
        "checkpoints": [
            pygame.Rect(1800, 100, 50, 50)  # Checkpoint a következő pályára
        ],
        "respawn": (500, 700)
    },
    {
        "platforms": [
            pygame.Rect(600, 800, 350, 20),
            pygame.Rect(1000, 600, 350, 20),
            pygame.Rect(1400, 400, 350, 20),
            pygame.Rect(1800, 200, 350, 20),
            pygame.Rect(0, 0, 50, SCREEN_HEIGHT),  # Bal fal
            pygame.Rect(SCREEN_WIDTH - 50, 0, 50, SCREEN_HEIGHT)  # Jobb fal
        ],
        "checkpoints": [
            pygame.Rect(1900, 150, 50, 50)  # Checkpoint a következő pályára
        ],
        "respawn": (600, 750)
    }
]

current_map_index = 0
platforms = maps[current_map_index]["platforms"]
checkpoints = maps[current_map_index]["checkpoints"]
respawn_point = maps[current_map_index]["respawn"]

player = Player()
bullets = []
last_shot_time = 0
shot_cooldown = 0.5

running = True
while running:
    screen.fill(BLACK)
    keys = pygame.key.get_pressed()
    
    # Eseménykezelés
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Bal egérgomb
            hook_rect = pygame.Rect(event.pos[0], event.pos[1], 1, 1)
            for platform in platforms:
                if hook_rect.colliderect(platform):
                    player.hook_x, player.hook_y = event.pos
                    player.hook_active = True
                    break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:  # 'E' gomb a grappling hook eltávolításához
            player.hook_active = False
            player.swinging = False
    
    # Karakter mozgás
    if player.move(keys, platforms, checkpoints):
        current_map_index = (current_map_index + 1) % len(maps)
        platforms = maps[current_map_index]["platforms"]
        checkpoints = maps[current_map_index]["checkpoints"]
        respawn_point = maps[current_map_index]["respawn"]
        player.respawn()
    
    # Lövés kezelése
    current_time = time.time()
    if current_time - last_shot_time > shot_cooldown:
        if keys[pygame.K_a]:
            bullets.append(Bullet(player.x, player.y + 20, "left"))
            last_shot_time = current_time
        if keys[pygame.K_d]:
            bullets.append(Bullet(player.x + 10, player.y + 20, "right"))
            last_shot_time = current_time
        if keys[pygame.K_w]:
            bullets.append(Bullet(player.x + 5, player.y, "up"))
            last_shot_time = current_time
        if keys[pygame.K_s]:
            bullets.append(Bullet(player.x + 5, player.y + 40, "down"))
            last_shot_time = current_time
    
    # Lövedékek mozgatása
    for bullet in bullets[:]:
        bullet.move()
        if bullet.x < 0 or bullet.x > SCREEN_WIDTH or bullet.y < 0 or bullet.y > SCREEN_HEIGHT:
            bullets.remove(bullet)
    
    # Kirajzolás
    player.draw(screen)
    for bullet in bullets:
        bullet.draw(screen)
    
    # Platformok kirajzolása
    for platform in platforms:
        pygame.draw.rect(screen, GREEN, platform)
    
    # Checkpointok kirajzolása
    for checkpoint in checkpoints:
        pygame.draw.rect(screen, RED, checkpoint)
    
    pygame.display.update()
pygame.quit()
