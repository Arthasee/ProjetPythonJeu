# Example file showing a basic pygame "game loop"
import pygame

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
pygame.font.init()
font = pygame.font.SysFont("Comic Sans MS",24)

w,h = 10,10
map = [[0 for x in range(w)] for y in range(h)]
map[0][0] = 1
colors = ["gray","red", "blue"] 

health = 9
zpressed=False
spressed=False

def renderhealthbar(health):
    bar_length = 400
    bar_height = 50
    bar_left = 0
    bar_top = screen.get_height()-bar_height
    surface=font.render(f"{health} / 10",False,"white")
    pygame.draw.rect(screen,"orange",(0,bar_top,bar_length,bar_height))
    pygame.draw.rect(screen,"red",(0,bar_top,health/10*bar_length,bar_height))
    screen.blit(surface,(bar_left + bar_length/2,bar_top + bar_height/2))
    return

def rendermap(carte,mouse_pos):
    width,height = 50,50
    xmax = 500
    ymax = 500
    for i in range(len(carte)):
        for j in range(len(carte)):
            pygame.draw.rect(screen,colors[carte[i][j]],pygame.Rect(i*width+5,j*height+5,width-5,height-5))
    if mouse_pos[0] >= xmax or mouse_pos[1] >= ymax :
        return
    #carte[int(mouse_pos[0]/50)][int(mouse_pos[1]/50)]=2
    pygame.draw.rect(screen,colors[2],pygame.Rect(int(mouse_pos[0]/50)*width+5,int(mouse_pos[1]/50)*height+5,width-5,height-5))
    return

def updatemap(mouse_pos,carte):
    xmax = 500
    ymax = 500
    if mouse_pos[0] >= xmax or mouse_pos[1] >= ymax :
        return
    carte[int(mouse_pos[0]/50)][int(mouse_pos[1]/50)]=2
    return

pygame.key.set_repeat(0,100000)

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("black")

    # RENDER YOUR GAME HERE
    mouse_pos = pygame.mouse.get_pos()
    rendermap(map,mouse_pos)
    renderhealthbar(health)
    #updatemap(mouse_pos,map)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_z]:
        health += 1 if (health<10 and not zpressed) else 0
        zpressed=True
    else :
        zpressed = False
    if keys[pygame.K_s]:
        health -= 1 if (health>0 and not spressed) else 0
        spressed=True
    else :
        spressed = False

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()