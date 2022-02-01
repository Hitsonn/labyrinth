import sys

from audio import *

from constants import *

from levels import GenerateLevel


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
        levels = i
        level = GenerateLevel()
        game = level.level_selection(levels)
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
                    if levels < 9:
                        levels += 1
                        game = level.level_selection(levels)
                        level_sound.stop()
                        won_sound.play()
                        show_message(screen, f"level {levels}")
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
            score = level.score()
        level_sound.stop()

    pygame.quit()


if __name__ == '__main__':
    main()
