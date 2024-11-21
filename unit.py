import pygame
import random

# Constantes
GRID_SIZE = 8
CELL_SIZE = 60
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE
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
        Attaque une unité cible.
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
        """Attaque une unité cible."""
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
    def __init__(self, pokemon):
        self.pokemon = pokemon
        self.x = 0
        self.y = 0
        self.nom = self.pokemon.nom
        self.pv = self.pokemon.stats[0]
        self.attaque = self.pokemon.stats[1]
        self.defense = self.pokemon.stats[2]
        self.att_spe = self.pokemon.stats[3]
        self.def_spe = self.pokemon.stats[4]
        self.vitesse = self.pokemon.stats[5]
        self.type = self.pokemon.type
        self.faiblesse = self.pokemon.faiblesses
        self.capacites = self.pokemon.capacites
        self.niveau = self.pokemon.niveau
    
    def attaquer(self, attaque, adversaire):
        CM = 1
        Eff = 1
        STAB = 1
        if random.randint(0, 100) <= attaque.precision:
            CM *= 1
        else :
            CM *= 0
        for types in adversaire.faiblesses:
            if attaque.Type == types:
                Eff *= 2
        if attaque.Type == adversaire.type:
            Eff *= 1/2   
        if attaque.Type == self.type:
            STAB *= 1.5
        CM *= Eff*STAB 
        adversaire.pv -= ((((self.niveau*0.4+2)*attaque.puissance*self.attaque)/adversaire.defense)/50 + 2)*CM


class Attaque:
    def __init__(self, nom, Type, puissance, precision, distance, niveau):
        self.nom = nom
        self.type = Type
        self.puissance = puissance
        self.precision = precision
        self.distance = distance
        self.niveau = niveau
    
class Salameche:
    def __init__(self):
        self.nom = "Salamèche"
        self.stats = [39,52,43,60,50,65]
        self.type = ["feu"]
        self.faiblesse = ["eau", "sol", "roche"]
        self.capacites = [Attaque("Griffe", "normal", 40, 100,1,1), Attaque("Rugissement", "normal", 0, 100,1,1)]
        self.niveau = 1