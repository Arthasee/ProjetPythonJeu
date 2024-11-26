"""Fichier avec les différentes Classes du jeu (Pokémon, Capacité)
    """
import random
import pygame

# Constantes
GRID_SIZE = 8
CELL_SIZE = 60
WIDTH = 768
HEIGHT = 640
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)


class Unit:
    """
    Classe pour représenter une unité.

    ...
    Attributs
    ---------
    x : int
        La position x de l'unité sur la grille.
    y : int
        La position y de l'unité sur la grille.
    health : int
        La santé de l'unité.
    attack_power : int
        La puissance d'attaque de l'unité.
    team : str
        L'équipe de l'unité ('player' ou 'enemy').
    is_selected : bool
        Si l'unité est sélectionnée ou non.

    Méthodes
    --------
    move(dx, dy)
        Déplace l'unité de dx, dy.
    attack(target)
        Capacite une unité cible.
    draw(screen)
        Dessine l'unité sur la grille.
    """

    def __init__(self, x, y, health, attack_power, team):
        """
        Construit une unité avec une position, une santé, une puissance d'attaque et une équipe.

        Paramètres
        ----------
        x : int
            La position x de l'unité sur la grille.
        y : int
            La position y de l'unité sur la grille.
        health : int
            La santé de l'unité.
        attack_power : int
            La puissance d'attaque de l'unité.
        team : str
            L'équipe de l'unité ('player' ou 'enemy').
        """
        self.x = x
        self.y = y
        self.health = health
        self.attack_power = attack_power
        self.team = team  # 'player' ou 'enemy'
        self.is_selected = False

    def move(self, dx, dy):
        """Déplace l'unité de dx, dy."""
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def attack(self, target):
        """Capacite une unité cible."""
        if abs(self.x - target.x) <= 1 and abs(self.y - target.y) <= 1:
            target.health -= self.attack_power

    def draw(self, screen):
        """Affiche l'unité sur l'écran."""
        color = BLUE if self.team == 'player' else RED
        if self.is_selected:
            pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE,
                             self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
        pygame.draw.circle(screen, color, (self.x * CELL_SIZE + CELL_SIZE //
                           2, self.y * CELL_SIZE + CELL_SIZE // 2), CELL_SIZE // 3)

class Pokemon:
    """Construit un pokémon spécifique avec sa position, ses statistiques, 
    ses capacités et son niveau
    """

    def __init__(self, pokemon, team, x, y):
        self.pokemon = pokemon
        self.team = team
        self.x = x
        self.y = y
        self.nom = pokemon.nom
        self.pv = self.pokemon.stats[0]
        self.attaque = self.pokemon.stats[1]
        self.defense = self.pokemon.stats[2]
        self.att_spe = self.pokemon.stats[3]
        self.def_spe = self.pokemon.stats[4]
        self.vitesse = self.pokemon.stats[5]
        self.type = self.pokemon.type
        self.faiblesse = self.pokemon.faiblesse
        self.capacites = self.pokemon.capacites
        self.niveau = self.pokemon.niveau
        self.is_selected = False
        self.image = pokemon.image

    def move(self, dx, dy):
        """Déplace l'unité de dx, dy."""
        if 0 <= self.x + dx < GRID_SIZE and 0 <= self.y + dy < GRID_SIZE:
            self.x += dx
            self.y += dy

    def draw(self, screen):
        """Affiche l'unité sur l'écran."""
        color = BLUE if self.team == 'player' else RED
        if self.is_selected:
            pygame.draw.rect(screen, color, (self.x * CELL_SIZE,
                             self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            screen.blit(self.image, (self.x*CELL_SIZE,self.y*CELL_SIZE))

    def attaquer(self, capacite, adversaire):
        """fonction qui calcule les points de vie de l'adversaire touché par l'attaque

        Args:
            capacite (Capacite): Classe de la capacité
            adversaire (Pokemon): Classe du pokémon adverse
        """
        cm = 1
        eff = 1
        stab = 1
        if random.randint(0, 100) <= capacite.precision:
            cm *= 1
        else :
            cm *= 0
        for types in adversaire.faiblesse:
            if capacite.type == types:
                eff *= 2
        if capacite.type == adversaire.type:
            eff *= 1/2
        if capacite.type == self.type:
            stab *= 1.5
        cm *= eff*stab
        adversaire.pv -= ((((self.niveau*0.4+2)*capacite.puissance*self.attaque)/adversaire.defense)/50 + 2)*cm

    def non_attaquer(self, capacite, adversaire):
        """fonction qui calcule la diminution ou l'augmentation des statistiques du pokémon

        Args:
            capacite (Capacite): Classe de la capacité utilisée
            adversaire (Pokemon): Classe du Pokémon, 
            peut être le pokémon attaquant lui-même si c'est un bonus
        """
        cm = 1
        if random.randint(0,100) <= capacite.precision:
            cm *= 1
        else :
            cm *= 0
        if capacite.stat == "attaque":
            adversaire.attaque *= capacite.puissance*cm
        elif capacite.stat == "defense":
            adversaire.defense *= capacite.puissance*cm
        elif capacite.stat == "att_spe":
            adversaire.att_spe *= capacite.puissance*cm
        elif capacite.stat == "def_spe":
            adversaire.def_spe *= capacite.puissance*cm
        elif capacite.stat == "vitesse":
            adversaire.vitesse *= capacite.puissance*cm

class Capacite:
    """Construit une capacité avec son type, sa puissance, sa précision, 
    la distance qu'elle peut accéder, le niveau à avoir pour la débloquer, 
    si la capacité est passive ou non, la statistique qu'elle touche si c'est une capacité passive
    """
    def __init__(self, nom, types, puissance, precision, distance, niveau, categorie, stat):
        self.nom = nom
        self.type = types
        self.puissance = puissance
        self.precision = precision
        self.distance = distance
        self.niveau = niveau
        self.categorie = categorie
        self.stat = stat

class Salameche:
    """Construit la classe du pokémon Salamèche avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Salamèche"
        self.stats = [39,52,43,60,50,65]
        self.type = ["feu"]
        self.faiblesse = ["eau", "sol", "roche"]
        self.capacites = [Capacite("Griffe", "normal", 40, 100,1,1,"attaque", None), Capacite("Rugissement", "normal", 2/3, 100,1,1, "non-attaque", "attaque")]
        self.niveau = 1
        self.image = [pygame.image.load("sprite/rfvf/4.png").convert_alpha(), pygame.image.load("sprite/rfvf/walk/o_hs_004_1.png").convert_alpha()]

class Carapuce:
    """Construit la classe du pokémon Carapuce avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Carapuce"
        self.stats = [44,48,65,50,64,43]
        self.type = ["eau"]
        self.faiblesse = ["plante", "electrik"]
        self.capacites = [Capacite("Charge", "normal", 35, 95, 1, 1, "attaque", None), Capacite("Mimi-Queue", "normal", 2/3, 100, 1, 1, "non-attaque", "defense")]
        self.niveau = 1
        self.image = [pygame.image.load("sprite/rfvf/7.png").convert_alpha()]

class Bulbizarre:
    """Construit la classe du pokémon Bulbizarre avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Bulbizarre"
        self.stats = [45, 49, 49, 65, 65, 45]
        self.type = ["plante, poison"]
        self.faiblesse = ["feu", "glace", "vol", "psy"]
        self.capacites = [Capacite("Charge", "normal", 35, 95, 1, 1, "attaque", None), Capacite("Rugissement", "normal", 2/3, 100,1,1, "non-attaque", "attaque")]
        self.niveau = 1
        self.image = [pygame.image.load("sprite/rfvf/1.png").convert()]
        
class Pikachu:
    """Construit la classe du pokémon Pikachu avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Pikachu"
        self.stats = [35,55,30,50,40,90]
        self.type = ["electrik"]
        self.faiblesse = ["sol"]
        self.capacites = [Capacite("Éclair", "electrik", 40, 100, 2, 1, "attaque", None), Capacite("Rugissement", "normal", 2/3, 100,1,1, "non-attaque", "attaque")]
        self.niveau = 1
        self.image = [pygame.image.load("sprite/rfvf/25.png")]