import pygame

class Screen:
    """
    Classe pour gérer l'affichage du jeu.

    Attributs
    ---------
    width : int
        Largeur de la fenêtre.
    height : int
        Hauteur de la fenêtre.
    title : str
        Titre de la fenêtre.
    background_color : tuple
        Couleur d'arrière-plan (par défaut noir).
    screen : pygame.Surface
        Surface principale de l'affichage.
    """

    def __init__(self, width, height, title="Mon jeu de stratégie", background_color=(0, 0, 0)):
        """
        Initialise la fenêtre du jeu.

        Paramètres
        ----------
        width : int
            Largeur de la fenêtre.
        height : int
            Hauteur de la fenêtre.
        title : str
            Titre de la fenêtre.
        background_color : tuple
            Couleur d'arrière-plan (par défaut noir).
        """
        self.width = width
        self.height = height
        self.title = title
        self.background_color = background_color #La couleur de l'arrière-plan de la fenêtre, définie par défaut (noir).

        # Initialisation de Pygame et de l'écran
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.title)
        self.clock = pygame.time.Clock()
        self.framerate = 60  # Fréquence d'images par seconde (FPS)

    def update(self):
        """Cette méthode est appelée pour mettre à jour l'affichage à chaque itération du jeu"""
        pygame.display.flip()  # Rafraîchit l'affichage
        self.clock.tick(self.framerate)  # Limite la vitesse du jeu à 60 FPS
        self.screen.fill(self.background_color)  # Remplit l'écran avec la couleur de fond

    def get_size(self):
        """Retourne la taille de la fenêtre."""
        return self.screen.get_size()

    def get_display(self):
        """Retourne la surface de l'écran."""
        return self.screen
