import os
import pygame
import pygame.freetype as freetype
import eyed3

# Import pygame.locals for easier access to key coordinates
# Updated to conform to flake8 and black standards

from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_SPACE,
    K_ESCAPE,
    KEYDOWN,
    QUIT,
)

BLACK = (0, 0, 0)
# GREEN = (0, 255, 0)
GREEN = (29, 185, 84)
WHITE = (255, 255, 255)

frontend_color = GREEN

# event to be set as mixer.music.set_endevent()
MUSIC_DONE = pygame.event.custom_type()

# Setup for sounds. Defaults are good.
pygame.mixer.init()

# Initialize pygame
pygame.init()

# Set up the clock for a decent framerate
clock = pygame.time.Clock()

# "Ininitializes a new pygame screen using the framebuffer"
# Based on "Python GUI in Linux frame buffer"
# http://www.karoltomala.com/blog/?p=679
disp_no = os.getenv("DISPLAY")
if disp_no:
    print("I'm running under X display = {0}".format(disp_no))

# Check which frame buffer drivers are available
# Start with fbcon since directfb hangs with composite output
drivers = ['fbcon', 'directfb', 'svgalib']
found = False
for driver in drivers:
    # Make sure that SDL_VIDEODRIVER is set
    if not os.getenv('SDL_VIDEODRIVER'):
        os.putenv('SDL_VIDEODRIVER', driver)
    try:
        pygame.display.init()
    except pygame.error:
        print('Driver: {0} failed.'.format(driver))
        continue
    found = True
    break

if not found:
    raise Exception('No suitable video driver found!')

size = (pygame.display.Info().current_w // 2, pygame.display.Info().current_h // 2)
print("Framebuffer size: %d x %d" % (size[0], size[1]))
#screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
screen = pygame.display.set_mode(size, pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE)

# Clear the screen to start
screen.fill((0, 0, 0))

# Initialise font support
# pygame.font.init()

# Render the screen
pygame.display.update()


# Variable to keep the main loop running
running = True

# test file
# mp3 = '03-i-dont-want-to-set-the-world-on-fire-the-ink-spots.mp3'
mp3 = 'makeba.mp3'
pygame.mixer.music.load(mp3)
song = pygame.mixer.Sound(mp3)

id3 = eyed3.load(mp3)
title = id3.tag.title

# change according to the display
freetype.set_default_resolution(72)

# create font object
font = freetype.Font('font/Montserrat-ExtraBold.ttf', 30)
# font = freetype.SysFont('Comic Sans MS', 30)
img = font.render('Now Playing!', frontend_color)[0]
pygame.draw.line(screen, frontend_color, (0, 40), (size[0], 40))


def draw_progress_bar(rect: pygame.rect, progress: float) -> pygame.surface:
    if progress < 0.:
        progress = 0.
    elif progress > 100.:
        progress = 100.

    surface = pygame.Surface((1000, 101))
    # surface.fill(GREEN)

    pygame.draw.arc(surface, frontend_color, (0, 0, 100, 100), 3.141/2., -3.141/2., width=1)
    pygame.draw.arc(surface, frontend_color, (1000-100, 0, 100, 100), -3.141/2., 3.141/2., width=1)
    pygame.draw.line(surface, frontend_color, (50,0), (1000 - 50, 0))
    pygame.draw.line(surface, frontend_color, (50, 100), (1000 - 50, 100))

    radius = 50
    x = (1000 - 2 * radius) / 100.0 * progress + radius
    pygame.draw.circle(surface, frontend_color, (x, 50), radius, width=0)

    x_scale = (rect[2] - rect[0]) / 1000.
    y_scale = (rect[3] - rect[1]) / 101.
    return pygame.transform.smoothscale_by(surface, (x_scale, y_scale))
    # return surface

screen.blit(img, (size[0]//2 - img.get_width() // 2, 0))
pygame.display.flip()

# start playing the file
pygame.mixer.music.play()
music_running = True

pygame.mixer.music.set_endevent(MUSIC_DONE)

# Main loop
while running:

    # Look at every event in the queue
    for event in pygame.event.get():

        # Did the user hit a key?
        if event.type == KEYDOWN:

            # Was it the Escape key? If so, stop the loop.
            if event.key == K_ESCAPE:
                running = False

            if event.key == K_SPACE:
                if music_running:
                    pygame.mixer.music.pause()
                    music_running = False
                else:
                    pygame.mixer.music.unpause()
                    music_running = True

        # Did the user click the window close button? If so, stop the loop.
        elif event.type == QUIT:
            running = False

    progress = pygame.mixer.music.get_pos() / (song.get_length() * 1000.0) * 100.
    print(progress)

    rect = (100, 50, size[0] - 100, 150)
    pbar = draw_progress_bar(rect, progress)
    screen.blit(pbar, (rect[0], rect[1]))
    # screen.blit(pbar, (0,0))
    pygame.display.flip()
    # pygame.display.update()

    clock.tick(30)

pygame.mixer.music.stop()
pygame.mixer.quit()
