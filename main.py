import os
import sys
import pygame


SIZE = WIN_WIDTH, WIN_HEIGHT = 800, 640
FPS = 60
PL_WIDTH, PL_HEIGHT = 32, 32

all_sprites = pygame.sprite.Group()
all_platforms = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()
all_portals = pygame.sprite.Group()
all_knives = pygame.sprite.Group()
pygame.mixer.init()
pygame.mixer.music.load('data/music.mp3')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.04)
levels = ['level1.txt', 'level2.txt']
screen = pygame.display.set_mode(SIZE)
clock = pygame.time.Clock()
pygame.init()


class Player(pygame.sprite.Sprite):
    right = True

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('data/hum.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PL_WIDTH, PL_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(x, y, PL_WIDTH, PL_HEIGHT)

        self.change_x = 0
        self.change_y = 0
        self.platforms = pygame.sprite.Group()
        self.image_kn = pygame.image.load('data/hum.png').convert_alpha()
        self.image_kn = pygame.transform.scale(self.image_kn, (PL_WIDTH, PL_HEIGHT))
        self.can_kill = False
        self.knives = pygame.sprite.Group()

    def gravity(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += 0.5
        if self.rect.y >= WIN_HEIGHT - self.rect.height and self.change_y > 0:
            self.change_y = 0
            self.rect.y = WIN_HEIGHT - self.rect.height

    def update(self):
        self.gravity()
        self.rect.x += self.change_x

        block_hit_list = pygame.sprite.spritecollide(self, self.platforms, False)
        for block in block_hit_list:
            if pygame.sprite.collide_mask(self, block):
                if self.change_x > 0:
                    self.rect.right = block.rect.left
                elif self.change_x < 0:
                    self.rect.left = block.rect.right
        self.rect.y += self.change_y
        block_hit_list = pygame.sprite.spritecollide(self, self.platforms, False)
        for block in block_hit_list:
            if pygame.sprite.collide_mask(self, block):
                if self.change_y > 0:
                    self.rect.bottom = block.rect.top
                elif self.change_y < 0:
                    self.rect.top = block.rect.bottom
                self.change_y = 0

    def jump(self):
        self.rect.y += 5
        platform_hit_list = pygame.sprite.spritecollide(self, self.platforms, False)
        self.rect.y -= 5

        if len(platform_hit_list) > 0 or self.rect.bottom >= WIN_HEIGHT:
            self.change_y = -14

    def go_left(self):
        self.change_x -= 6
        if self.right:
            self.flip()
            self.right = False

    def go_right(self):
        self.change_x += 6
        if not self.right:
            self.flip()
            self.right = True

    def stop(self):
        self.change_x = 0

    def flip(self):
        self.image = pygame.transform.flip(self.image, True, False)


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("data/pl.png")
        self.image = pygame.transform.scale(self.image, (PL_WIDTH, PL_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(x, y, PL_WIDTH, PL_HEIGHT)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("data/enemy.png")
        self.image = pygame.transform.scale(self.image, (PL_WIDTH, PL_HEIGHT)).convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(x, y, PL_WIDTH, PL_HEIGHT)


class Portals(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("data/portal.png")
        self.image = pygame.transform.scale(self.image, (PL_WIDTH, PL_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(x, y, PL_WIDTH, PL_HEIGHT)


class Knife(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("data/knife.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (PL_WIDTH, PL_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = pygame.Rect(x, y, PL_WIDTH, PL_HEIGHT)


def start_screen():
    intro_text = ["Марио",
                  "Управление:",
                  "Стрелочки работают по своему назначению",
                  "SPACE - начать игру и перезапустить её"]
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIN_WIDTH, WIN_HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def main():
    pygame.init()
    pygame.display.set_caption("Mario")
    player = generate_level(load_level(levels[0]))
    bg = load_image('bg.jpg')
    bg = pygame.transform.scale(bg, (WIN_WIDTH, WIN_HEIGHT))
    end = load_image('game over.png')
    end = pygame.transform.scale(end, (WIN_WIDTH, WIN_HEIGHT))
    win = load_image('win.jpg')
    win = pygame.transform.scale(win, (WIN_WIDTH, WIN_HEIGHT))
    current_level_index = 0
    player.platforms = all_platforms
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()
                if event.key == pygame.K_SPACE:
                    clear_text()
                    player = generate_level(load_level(levels[0]))
                    current_level_index = 0
                    player.platforms = all_platforms
                    bg = load_image('bg.jpg')
                    bg = pygame.transform.scale(bg, (WIN_WIDTH, WIN_HEIGHT))

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()

        all_sprites.update()

        if player.rect.right > WIN_WIDTH:
            player.rect.right = WIN_WIDTH

        if player.rect.left < 0:
            player.rect.left = 0

        if pygame.sprite.spritecollide(player, all_knives, False):
            for knife in all_knives:
                player.can_kill = True
                player.image = player.image_kn
                knife.kill()

        if pygame.sprite.spritecollide(player, all_enemies, False):
            for enemy in pygame.sprite.spritecollide(player, all_enemies, False):
                if player.can_kill:
                    enemy.kill()
                else:
                    cursor = pygame.sprite.Sprite(all_sprites)
                    cursor.image = end
                    cursor.rect = cursor.image.get_rect()

        if pygame.sprite.spritecollide(player, all_portals, False):
            clear_text()
            current_level_index += 1
            if current_level_index == len(levels):
                cursor = pygame.sprite.Sprite(all_sprites)
                cursor.image = win
                cursor.rect = cursor.image.get_rect()
            else:
                player = generate_level(load_level(levels[current_level_index]))
                player.platforms = all_platforms
                bg = load_image('bg.jpg')
                bg = pygame.transform.scale(bg, (WIN_WIDTH, WIN_HEIGHT))

        screen.blit(bg, (0, 0))
        all_sprites.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


def load_image(name):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    fullname = os.path.join('data', filename)
    if not os.path.isfile(fullname):
        print(f"Файл '{fullname}' не найден")
        sys.exit()
    with open(fullname, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    return level_map


def generate_level(level):
    new_player = None
    x = y = 0
    for row in level:
        for col in row:
            if col == "-":
                pf = Platform(x, y)
                all_sprites.add(pf)
                all_platforms.add(pf)
            elif col == '@':
                new_player = Player(x, y)
                all_sprites.add(new_player)
            elif col == "&":
                en = Enemy(x, y)
                all_sprites.add(en)
                all_enemies.add(en)
            elif col == "*":
                po = Portals(x, y)
                all_sprites.add(po)
                all_portals.add(po)
            if col == "!":
                kn = Knife(x, y)
                all_sprites.add(kn)
                all_knives.add(kn)
            x += PL_WIDTH
        y += PL_HEIGHT
        x = 0
    return new_player


def clear_text():
    all_sprites.empty()
    all_platforms.empty()
    all_enemies.empty()
    all_portals.empty()


start_screen()
if __name__ == "__main__":
    sys.exit(main())