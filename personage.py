import pytmx
import pygame
from constants import*


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
        if pygame.key.get_pressed()[pygame.K_LEFT] or pygame.key.get_pressed()[pygame.K_a]:
            next_x -= 1
            self.hero.update_image_left()
        if pygame.key.get_pressed()[pygame.K_RIGHT] or pygame.key.get_pressed()[pygame.K_d]:
            next_x += 1
            self.hero.update_image_right()
        if pygame.key.get_pressed()[pygame.K_UP] or pygame.key.get_pressed()[pygame.K_w]:
            next_y -= 1
            self.hero.update_image_up()
        if pygame.key.get_pressed()[pygame.K_DOWN] or pygame.key.get_pressed()[pygame.K_s]:
            next_y += 1
            self.hero.update_image_down()
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


class Hero:

    def __init__(self, pic, position):
        self.pic = pic
        self.x, self.y = position
        self.image = pygame.image.load(f"images/{pic}")

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image, (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))

    def update_image_left(self):
        self.image = pygame.image.load(f"images/l_hero.png")

    def update_image_right(self):
        self.image = pygame.image.load(f"images/{self.pic}")

    def update_image_up(self):
        self.image = pygame.image.load(f"images/u_hero.png")

    def update_image_down(self):
        self.image = pygame.image.load(f"images/d_hero.png")


class Enemy:

    def __init__(self, pic, position, delay=300):
        self.x, self.y = position
        self.delay = delay
        pygame.time.set_timer(ENEMY_EVENT_TYPE, self.delay)
        self.image = pygame.image.load(f"images/{pic}")

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image, (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))


class Bonus:

    def __init__(self, position):
        self.x, self.y = position
        self.image = pygame.image.load(f"images/close_bonus.png")
        self.score = 0

    def get_position(self):
        return self.x, self.y

    def set_position(self, position):
        self.x, self.y = position

    def render(self, screen):
        delta = (self.image.get_width() - TILE_SIZE) // 2
        screen.blit(self.image, (self.x * TILE_SIZE - delta, self.y * TILE_SIZE - delta))

    def activation(self):
        self.image = pygame.image.load(f"images/open_bonus.png")
        self.score = 100

    def score(self):
        return self.score
