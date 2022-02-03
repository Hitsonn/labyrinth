import pygame

pygame.mixer.init()

start_sound = pygame.mixer.Sound(f"audio/start.mp3")
start_sound.set_volume(0.2)

level_sound = pygame.mixer.Sound(f"audio/level.mp3")
level_sound.set_volume(0.2)

stop_sound = pygame.mixer.Sound(f"audio/stop.mp3")
stop_sound.set_volume(0.2)

over_sound = pygame.mixer.Sound(f"audio/over.mp3")
stop_sound.set_volume(0.2)

won_sound = pygame.mixer.Sound(f"audio/won.mp3")
won_sound.set_volume(0.5)

pause_sound = pygame.mixer.Sound(f"audio/pause.mp3")
pause_sound.set_volume(0.2)
