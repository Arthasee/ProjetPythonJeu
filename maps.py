import pygame
import pytmx
import pyscroll

class Map:
    def __init__(self, screen):
        """Initialise la carte avec l'écran Pygame."""
        self.screen = screen  # L'écran sur lequel la carte sera dessinée
        self.tmx_data = None  # Données de la carte TMX
        self.map_layer = None  # Calque de la carte
        self.group = None  # Groupe de rendu pour la carte
        self.switch_map("map")  # Charge la carte par défaut

    def switch_map(self, map: str):
        """
        Charge une nouvelle carte TMX en fonction du nom de fichier donné.

        Paramètre
        ---------
        map : str
            Le nom du fichier TMX à charger (par exemple 'map_1').
        """
        # Charge le fichier TMX avec le chemin absolu ou relatif
        
        
        # Charge les données TMX depuis un fichier (ici 'map_1.tmx')
        self.tmx_data = pytmx.load_pygame("map_1.tmx")   

        # Crée un objet TiledMapData à partir des données TMX
        map_data = pyscroll.data.TiledMapData(self.tmx_data)

        # Utilise le renderer BufferedRenderer pour dessiner la carte
        self.map_layer = pyscroll.BufferedRenderer(map_data, self.screen.get_size())

        # Crée un groupe Pyscroll pour gérer l'affichage de la carte et autres objets
        # default_layer=7 signifie que nous avons défini le calque de base à 7, vous pouvez ajuster en fonction des besoins
        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer, default_layer=10)

    def update(self):
        """Met à jour l'affichage de la carte."""
        # Dessine la carte sur l'écran avec les informations du groupe (les éléments du groupe sont affichés ici)
        self.group.draw(self.screen)  # Utilise self.screen qui est déjà une surface Pygame

