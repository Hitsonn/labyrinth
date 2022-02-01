import sys

from audio import *

from constants import *

from personage import Hero, Enemy, Bonus, Labyrinth, Game

pygame.init()

pygame.mixer.init()

all_bonus = []


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
    global all_bonus
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
    score = 0
    pygame.init()
    screen = pygame.display.set_mode(WINDOWS_SIZE)
    clock = pygame.time.Clock()
    start_sound.play()
    start_screen(screen, INTRO_TEXT, '1')
    game_over = False
    is_paused = False
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
                if event.type == ENEMY_EVENT_TYPE and not game_over and not is_paused:
                    game.move_enemy()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        is_paused = not is_paused
            if not is_paused:
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
        for bonus in all_bonus:
            score += bonus.score
        level_sound.stop()

    pygame.quit()


if __name__ == '__main__':
    main()
