import pygame
import pytmx
import pyscroll
from constante import *

class Map:
    def __init__(self, screen, map):
        """Initialise la carte avec l'écran Pygame."""
        self.screen = screen  # L'écran sur lequel la carte sera dessinée
        self.tmx_data = None  # Données de la carte TMX
        self.map_layer = None  # Calque de la carte
        self.group = None  # Groupe de rendu pour la carte
        self.map = map # la carte sélectionnée
        self.switch_map()  # Charge la carte par défaut
        # Initialisation des collisions
        self.collisions = []
        self._load_collisions()

    def switch_map(self):
        """
        Charge une nouvelle carte TMX en fonction du nom de fichier donné.

        Paramètre
        ---------
        map : str
            Le nom du fichier TMX à charger (par exemple 'map_1').
        """
        # Charge le fichier TMX avec le chemin absolu ou relatif
        
        
        # Charge les données TMX depuis un fichier (ici 'map_1.tmx')
        self.tmx_data = pytmx.load_pygame(self.map)   

        # Crée un objet TiledMapData à partir des données TMX
        map_data = pyscroll.data.TiledMapData(self.tmx_data)

        # Facteur de zoom (Mise à l'échelle grille Abithan)
        tile_width = self.tmx_data.tilewidth
        tile_height = self.tmx_data.tileheight
        zoom = CELL_SIZE / tile_width

        # Utilise le renderer BufferedRenderer pour dessiner la carte
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size(), clamp_camera=True)
        self.map_layer.zoom = zoom
        # Crée un groupe Pyscroll pour gérer l'affichage de la carte et autres objets
        # default_layer=7 signifie que nous avons défini le calque de base à 7, vous pouvez ajuster en fonction des besoins
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=10)
        
    def _load_collisions(self):
        """Charge les objets de collision depuis Tiled et les ajuste à la grille."""
        self.collisions = []
        for obj in self.tmx_data.objects:
            if obj.type == "collision":
                grid_x = int(obj.x // CELL_SIZE)
                grid_y = int(obj.y // CELL_SIZE)
                grid_width = int(obj.width // CELL_SIZE)
                grid_height = int(obj.height // CELL_SIZE)
                rect = pygame.Rect(grid_x * CELL_SIZE, grid_y * CELL_SIZE, grid_width * CELL_SIZE, grid_height * CELL_SIZE)
                self.collisions.append(rect)
                
                print(f"Collision ajustée : {rect}")  # Debugging




    
    def update(self):
        """Dessine la carte et les collisions (pour debug)."""
        self.group.draw(self.screen)
        
         # Dessiner les zones de collision pour debug
        for rect in self.collisions:
            pygame.draw.rect(self.screen, (255, 0, 0), rect, 2)  # Rouge pour visualiser les collisions

