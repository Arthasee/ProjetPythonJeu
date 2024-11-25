# Example file showing a circle moving on screen
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
dt = 0
screencolor = ["purple","blue","red","brown"]
colorindex = 0
speed = 600
slow = 150
sprite=pygame.image.load("sprite.png")

player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN :
            colorindex = colorindex + 1 if colorindex < len(screencolor)-1 else 0

    # fill the screen with a color to wipe away anything from last frame
    screen.fill(screencolor[colorindex])

    screen.blit(sprite, player_pos)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_z]:
        player_pos.y -= speed * dt
    if keys[pygame.K_s]:
        player_pos.y += speed * dt
    if keys[pygame.K_q]:
        player_pos.x -= slow * dt
    if keys[pygame.K_d]:
        player_pos.x += slow * dt

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(60) / 1000

pygame.quit()