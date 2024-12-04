# Constantes
GRID_WIDTH = 32
GRID_HEIGHT = 24
CELL_SIZE = 32
TOTAL_HEIGHT = GRID_HEIGHT * CELL_SIZE #Permet avoir hauteur
TOTAL_WIDTH = int(TOTAL_HEIGHT * 16/9) # Permet avoir largeur proportionnel au 16/9 format d'écran standard (bien que la carte soit en 32*24, permet d'intégrer ATH)
MAP_WIDTH = GRID_WIDTH * CELL_SIZE
ATH_WIDTH = TOTAL_WIDTH - MAP_WIDTH + 60
MAX_DISTANCE = 6 # limite de déplacement
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)