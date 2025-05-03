import pygame
import random
from pygame import mixer, font, transform, image, key, event, display, QUIT, KEYDOWN, K_SPACE, K_LEFT, K_RIGHT

# Инициализация
pygame.init()
mixer.init()

# Звуки
mixer.music.load('space.ogg')
mixer.music.play(-1)
fire_sound = mixer.Sound('fire.ogg')

# Шрифты
font.init()
stats_font = font.Font(None, 36)
game_over_font = pygame.font.Font(None, 100)
text_lose = game_over_font.render('GAME OVER', True, (180, 0, 0))
text_win = game_over_font.render('YOU WIN!', True, (0, 180, 0))

# Настройки окна
win_width = 1000  # Увеличенный размер окна
win_height = 700
display.set_caption("Cosmic Shooter")
window = display.set_mode((win_width, win_height))
background = transform.scale(image.load("galaxy.jpg"), (win_width, win_height))

# Игровые переменные
lost = 0
win = 0
health = 3
level = 1

# Группы спрайтов
monsters = pygame.sprite.Group()
bullets = pygame.sprite.Group()
asteroids = pygame.sprite.Group()

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_width - 80:
            self.rect.x += self.speed

    def fire(self):
        if len(bullets) < 3:  # Ограничение на количество пуль
            bullet = Bullet("bullet.png", self.rect.centerx, self.rect.top, 16, 21, -15)
            bullets.add(bullet)
            fire_sound.play()

class Enemy(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.speed = random.randint(1, 3) + level  # Увеличиваем скорость с уровнем

    def update(self):
        self.rect.y += self.speed
        global lost
        if self.rect.y > win_height:
            lost += 1
            self.rect.y = 0
            self.rect.x = random.randint(100, win_width - 100)

class Asteroid(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        # Добавляем случайное вращение
        self.rotation = 0
        self.rotation_speed = random.randint(-3, 3)
        self.original_image = transform.scale(image.load(player_image), (size_x, size_y))

    def update(self):
        self.rect.y += self.speed
        # Вращение астероида
        self.rotation = (self.rotation + self.rotation_speed) % 360
        self.image = transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        if self.rect.y > win_height:
            self.rect.y = 0
            self.rect.x = random.randint(100, win_width - 100)

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

# Создание игрока
ship = Player("rocket.png", win_width // 2, win_height - 100, 80, 100, 10)

# Функция создания врагов
def create_enemies():
    monsters = pygame.sprite.Group()
    for i in range(5 + level * 2):  # Увеличиваем количество с уровнем
        monster = Enemy("ufo.png", random.randint(100, win_width - 100), 
                       random.randint(-300, 0), 80, 60, random.randint(1, 3))
        monsters.add(monster)
    return monsters

# Функция создания астероидов
def create_asteroids():
    asteroids = pygame.sprite.Group()
    for i in range(2 + level):  # Увеличиваем количество с уровнем
        asteroid = Asteroid("asteroid.png", random.randint(100, win_width - 100),
                           random.randint(-500, -100), 90, 90, random.randint(1, 2))
        asteroids.add(asteroid)
    return asteroids

# Создание начальных врагов и астероидов
monsters = create_enemies()
asteroids = create_asteroids()

# Игровой цикл
run = True
finish = False
clock = pygame.time.Clock()

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE and not finish:
                ship.fire()
            if e.key == K_SPACE and finish:  # Рестарт игры
                finish = False
                lost = 0
                win = 0
                health = 3
                level = 1
                monsters = create_enemies()
                asteroids = create_asteroids()
                ship.rect.x = win_width // 2
                ship.rect.y = win_height - 100
    
    if not finish:
        window.blit(background, (0, 0))
        
        # Отображение статистики
        stats = [
            f"Missed: {lost}",
            f"Killed: {win}",
            f"Health: {health}",
            f"Level: {level}"
        ]
        
        for i, stat in enumerate(stats):
            text = stats_font.render(stat, True, (255, 255, 255))
            window.blit(text, (10, 10 + i * 40))
        
        # Обновление и отрисовка спрайтов
        monsters.update()
        asteroids.update()
        bullets.update()
        ship.update()
        
        monsters.draw(window)
        asteroids.draw(window)
        bullets.draw(window)
        ship.reset()
        
        # Проверка столкновений пуль с врагами
        if pygame.sprite.groupcollide(monsters, bullets, True, True):
            win += 1
            if win % 10 == 0:  # Каждые 10 убитых - новый уровень
                level += 1
                monsters = create_enemies()
                asteroids = create_asteroids()
            else:
                monsters.add(Enemy("ufo.png", random.randint(100, win_width - 100), 
                                 random.randint(-300, 0), 80, 60, random.randint(1, 3)))
        
        # Проверка столкновений пуль с астероидами
        if pygame.sprite.groupcollide(asteroids, bullets, True, True):
            lost = max(0, lost - 2)  # Уменьшаем счетчик пропущенных
            asteroids.add(Asteroid("asteroid.png", random.randint(100, win_width - 100),
                          random.randint(-500, -100), 90, 90, random.randint(1, 2)))
        
        # Проверка столкновений игрока
        if pygame.sprite.spritecollide(ship, monsters, False) or pygame.sprite.spritecollide(ship, asteroids, False):
            health -= 1
            if health <= 0:
                finish = True
            else:
                # "Мигание" при получении урона
                ship.image.set_alpha(100)
                pygame.time.delay(200)
                ship.image.set_alpha(255)
                ship.rect.x = win_width // 2
        
        # Условия победы/проигрыша
        if lost >= 5:
            finish = True
        
        if win >= 10 * level:  # Для перехода на след. уровень нужно больше убить
            finish = True
            window.blit(text_win, (win_width//2 - 150, win_height//2 - 50))
            pygame.display.update()
            pygame.time.delay(2000)
            level += 1
            finish = False
            monsters = create_enemies()
            asteroids = create_asteroids()
    
    else:
        # Экран завершения игры
        if health <= 0 or lost >= 5:
            window.blit(text_lose, (win_width//2 - 180, win_height//2 - 50))
        else:
            window.blit(text_win, (win_width//2 - 150, win_height//2 - 50))
        
        restart_text = stats_font.render("Press SPACE to restart", True, (255, 255, 255))
        window.blit(restart_text, (win_width//2 - 100, win_height//2 + 100))
    
    pygame.display.update()
    clock.tick(60)

pygame.quit()