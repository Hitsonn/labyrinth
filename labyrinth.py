import sys
import time

import pytmx
from audio import *

pygame.init()
pygame.mixer.init()

WINDOWS_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT = 672, 648
FPS = 10
MAPS_DIR = "maps"
TILE_SIZE = 32
ENEMY_EVENT_TYPE = 30
NUMBER_OF_LEVELS = 9
INTRO_TEXT = ["PACMAN 2022", "", "", "", "",
                  "", "", "", "", "",
                  "для продолжения",
                  "нажми любую клавишу...",
                  ]
FINAL_TEXT = ["PACMAN 2022", "", "", "", "",
                  "", "", "", "",
                  "спасибо за игру",
                  "для выхода",
                  "нажми любую клавишу...",
                  ]
IS_PAUSED = False


class Labyrinth:

    def __init__(self, filename, free_tiles, finish_tile):
        self.map = pytmx.load_pygame(f"{MAPS_DIR}/{filename}")
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tiles = free_tiles
        self.finish_tile = finish_tile

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))

    def get_tile_id(self, position):
        return self.map.tiledgidmap[self.map.get_tile_gid(*position, 0)]

    def is_free(self, position):
        return self.get_tile_id(position) in self.free_tiles

    def find_path_step(self, start, target):
        INF = 1000
        x, y = start
        distance = [[INF] * self.width for _ in range(self.height)]
        distance[y][x] = 0
        prev = [[None] * self.width for _ in range(self.height)]
        queue = [(x, y)]
        while queue:
            x, y = queue.pop(0)
            for dx, dy in (1, 0), (0, 1), (-1, 0), (0, -1):
                next_x, next_y = x + dx, y + dy
                if 0 <= next_x < self.width and 0 < next_y < self.height and \
                        self.is_free((next_x, next_y)) and distance[next_y][next_x] == INF:
                    distance[next_y][next_x] = distance[y][x] + 1
                    prev[next_y][next_x] = (x, y)
                    queue.append((next_x, next_y))
        x, y = target
        if distance[y][x] == INF or start == target:
            return start
        while prev[y][x] != start:
            x, y = prev[y][x]
        return x, y


class Hero:

    def __init__(self, pic, position):
        self.x, self.y = position
        self.image = pygame.image.load(f"images/{pic}")

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image, (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))


class Enemy:

    def __init__(self, pic, position, delay=300):
        self.x, self.y = position
        self.delay = delay
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)
        self.image = pygame.image.load(f"images/{pic}")

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        if not IS_PAUSED:
            self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image, (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))


class Bonus:

    def __init__(self, position):
        self.x, self.y = position
        self.image = pygame.image.load(f"images/close_bonus.png")

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        if not IS_PAUSED:
            self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image, (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))

    def activation(self):
        self.image = pygame.image.load(f"images/open_bonus.png")


class Game:
    def __init__(self, labyrinth, hero, enemy, bonus):
        self.labyrinth = labyrinth
        self.hero = hero
        self.enemy = enemy
        self.bonus = bonus
        self.score = 0
        self.result = False
        self.all_sprites = pygame.sprite.Group()

    def render(self, screen):
        self.labyrinth.render(screen)
        self.hero.render(screen)
        for bonus in self.bonus:
            bonus.render(screen)
        for enemy in self.enemy:
            enemy.render(screen)

    def update_hero(self):
        next_x, next_y = self.hero.get_position()
        if pygame.key.get_pressed()[pygame.K_LEFT]:
            next_x -= 1
        if pygame.key.get_pressed()[pygame.K_RIGHT]:
            next_x += 1
        if pygame.key.get_pressed()[pygame.K_UP]:
            next_y -= 1
        if pygame.key.get_pressed()[pygame.K_DOWN]:
            next_y += 1
        if self.labyrinth.is_free((next_x, next_y)):
            self.hero.set_position((next_x, next_y))

    def move_enemy(self):
        for enemy in self.enemy:
            next_position = self.labyrinth.find_path_step(enemy.get_position(),
                                                          self.hero.get_position())
            enemy.set_position(next_position)

    def move_bonus(self):
        for bonus in self.bonus:
            next_position = self.labyrinth.find_path_step(bonus.get_position(),
                                                          self.hero.get_position())
            bonus.set_position(next_position)

    def check_win(self):
        pygame.mixer.music.stop()
        return self.labyrinth.get_tile_id(self.hero.get_position()) == self.labyrinth.finish_tile

    def check_lose(self):
        for enemy in self.enemy:
            if self.hero.get_position() == enemy.get_position():
                self.result = True
                pygame.mixer.music.stop()
        return self.result

    def check_bonus(self):
        for bonus in self.bonus:
            if self.hero.get_position() == bonus.get_position():
                self.score = 100
                bonus.activation()

    def check_score(self):
        return self.score


def play_audio(track):
    pygame.mixer.music.load(f"audio\{track}")
    pygame.mixer.music.play(1)
    pygame.mixer.music.set_volume(0.3)


def start_screen(screen, text, message):
    clock = pygame.time.Clock()
    fon = pygame.transform.scale(pygame.image.load(f"images/background.jpg"), WINDOWS_SIZE)
    screen.blit(fon, (0, 0))
    font = pygame.font.Font('fonts/PeaceSans.otf', 30)
    text_coord = 10
    message = message
    for line in text:
        string_rendered = font.render(line, True, pygame.Color('#00416a'), pygame.Color('#71bc78'))
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
            elif event.type == pygame.KEYDOWN:
                if message:
                    show_message(screen, f"level {message}")
                    pygame.display.flip()
                    clock.tick(1)
                return
        pygame.display.flip()
        clock.tick(FPS)


def show_score(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, (50, 70, 0))
    text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
    text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2 - 100
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (200, 150, 50), (text_x - 10, text_y - 10,
                                              text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


def show_message(screen, message):
    font = pygame.font.Font(None, 50)
    text = font.render(message, True, (50, 70, 0))
    text_x = WINDOW_WIDTH // 2 - text.get_width() // 2
    text_y = WINDOW_HEIGHT // 2 - text.get_height() // 2
    text_w = text.get_width()
    text_h = text.get_height()
    pygame.draw.rect(screen, (200, 150, 50), (text_x - 10, text_y - 10,
                                              text_w + 20, text_h + 20))
    screen.blit(text, (text_x, text_y))


def generate_level(level):
    level = level
    speed_enemy = 300
    labirinth_1 = Labyrinth("map1.tmx", [10, 46], 46)
    labirinth_2 = Labyrinth("map2.tmx", [15, 46], 46)
    labirinth_3 = Labyrinth("map3.tmx", [30, 46], 46)
    hero = Hero("hero.png", (10, 9))
    enemy_1 = Enemy("enemy.png", (19, 9), speed_enemy)
    enemy_2 = Enemy("enemy.png", (1, 7), speed_enemy)
    enemy_3 = Enemy("enemy.png", (4, 7), speed_enemy)
    bonus_1 = Bonus((17, 5))
    bonus_2 = Bonus((19, 17))
    bonus_3 = Bonus((1, 1))
    bonus_4 = Bonus((9, 9))
    bonus_5 = Bonus((9, 9))
    bonus_6 = Bonus((9, 9))
    all_bonus = [bonus_1, bonus_2, bonus_3, bonus_4, bonus_5, bonus_6]
    if level == 1:
        game = Game(labirinth_1, hero, [enemy_1], [bonus_1])
    elif level == 2:
        game = Game(labirinth_2, hero, [enemy_1], [bonus_2])
    elif level == 3:
        game = Game(labirinth_3, hero, [enemy_1], [bonus_3])
    elif level == 4:
        game = Game(labirinth_1, hero, [enemy_1, enemy_2], [bonus_1, bonus_2])
    elif level == 5:
        game = Game(labirinth_2, hero, [enemy_1, enemy_2], [bonus_1])
    elif level == 6:
        game = Game(labirinth_3, hero, [enemy_1, enemy_2], [bonus_1])
    elif level == 7:
        game = Game(labirinth_1, hero, [enemy_1, enemy_2, enemy_3], [bonus_1])
    elif level == 8:
        game = Game(labirinth_2, hero, [enemy_1, enemy_2, enemy_3], [bonus_1])
    elif level == 9:
        game = Game(labirinth_3, hero, [enemy_1, enemy_2, enemy_3], [bonus_1])
    return game


def terminate():
    level_sound.stop()
    stop_sound.play()
    screen = pygame.display.set_mode(WINDOWS_SIZE)
    start_screen(screen, FINAL_TEXT, None)
    pygame.quit()
    sys.exit()


def main():
    global IS_PAUSED
    score = 0
    pygame.init()
    screen = pygame.display.set_mode(WINDOWS_SIZE)
    clock = pygame.time.Clock()
    start_sound.play()
    start_screen(screen, INTRO_TEXT, '1')
    game_over = False
    for i in range(1, NUMBER_OF_LEVELS + 1):
        show_score(screen, f" Bonus = {score}")
        pygame.display.flip()
        clock.tick(1)
        level = i
        game = generate_level(level)
        start_sound.stop()
        level_sound.play()
        while True:
            game.check_bonus()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == ENEMY_EVENT_TYPE and not game_over:
                    game.move_enemy()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        IS_PAUSED = not IS_PAUSED
            if not IS_PAUSED:
                if not game_over:
                    game.update_hero()
                screen.fill((0, 0, 0))
                game.render(screen)
                if game.check_win():
                    if level < 9:
                        level += 1
                        generate_level(level)
                        level_sound.stop()
                        won_sound.play()
                        show_message(screen, f"level {level}")
                        pygame.display.flip()
                        clock.tick(1)
                        break
                    else:
                        level_sound.stop()
                        start_sound.play()
                        game_over = True
                        show_message(screen, "You win!")
                        pygame.display.flip()
                        clock.tick(1)
                        start_screen(screen, INTRO_TEXT, None)
                        break
                if game.check_lose():
                    level_sound.stop()
                    game_over = True
                    show_message(screen, "You lose!")
                pygame.display.flip()
                clock.tick(FPS)
        score += game.score
        level_sound.stop()

    pygame.quit()


if __name__ == '__main__':
    main()
