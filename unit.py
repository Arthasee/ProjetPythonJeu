"""Fichier avec les différentes Classes du jeu (Pokémon, Capacité)
    """
import random
import pygame
from constante import *


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
        self.nerfs = {
            "attaque": 0,
            "defense": 0,
            "vitesse": 0,
            "attaque_spé": 0,
            "defense_spé": 0
        }
        self.type = self.pokemon.type
        self.faiblesse = self.pokemon.faiblesse
        self.capacites = self.pokemon.capacites
        self.niveau = self.pokemon.niveau
        self.is_selected = False
        self.image = pokemon.image
        self.image = pygame.transform.scale(self.image, (CELL_SIZE, CELL_SIZE)) # Redimensionner les sprites

    def move(self, dx, dy):
        """Déplace l'unité de dx, dy."""
        if 0 <= self.x + dx < GRID_WIDTH and 0 <= self.y + dy < GRID_HEIGHT:
            self.x += dx
            self.y += dy

    def draw(self, screen):
        """Affiche l'unité sur l'écran."""
        # color = BLUE if self.team == 'player' else RED
        if self.is_selected:
            pygame.draw.rect(screen, GREEN, (self.x * CELL_SIZE,self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE),2)
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
        damage = ((((self.niveau * 0.4 + 2) * capacite.puissance * self.attaque) / adversaire.defense) / 50 + 2) * cm
        adversaire.pv = max(0, adversaire.pv - damage)  # Empêche les PV d'être négatifs

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
            if capacite.categorie == "non-attaque":
                # Appliquer la baisse à l'adversaire
                adversaire.appliquer_nerf(capacite.stat)
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

    def appliquer_nerf(self, stat):
        """Applique un nerf à la statistique spécifiée par l'attaque."""
        if stat in self.nerfs:
            self.nerfs[stat] += 1

class Capacite:
    """Construit une capacité avec son type, sa puissance, sa précision, 
    la distance qu'elle peut accéder, le niveau à avoir pour la débloquer, 
    si la capacité est passive ou non, la statistique qu'elle touche si c'est une capacité passive
    """
    def __init__(self, nom, types, puissance, precision, distance, niveau, categorie, stat, cout_pa):
        self.nom = nom
        self.type = types
        self.puissance = puissance
        self.precision = precision
        self.distance = distance
        self.niveau = niveau
        self.categorie = categorie
        self.stat = stat
        self.cout_pa = cout_pa

class Salameche:
    """Construit la classe du pokémon Salamèche avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Salamèche"
        self.stats = [39,52,43,60,50,65]
        self.type = ["feu"]
        self.faiblesse = ["eau", "sol", "roche"]
        self.capacites = [Capacite("Griffe", "normal", 40, 100,1,1,"attaque", None, 6), Capacite("Rugissement", "normal", 2/3, 100,1,1, "non-attaque", "attaque", 6)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/salameche.png") #sprite/rfvf/4.png
        # self.walk = [pygame.image.load("sprite/rfvf/walk/o_hs_004_1.png").convert_alpha(), ]

class Carapuce:
    """Construit la classe du pokémon Carapuce avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Carapuce"
        self.stats = [44,48,65,50,64,43]
        self.type = ["eau"]
        self.faiblesse = ["plante", "electrik"]
        self.capacites = [Capacite("Charge", "normal", 35, 95, 1, 1, "attaque", None, 6), Capacite("Mimi-Queue", "normal", 2/3, 100, 1, 1, "non-attaque", "defense", 6)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/carapuce.png")

class Bulbizarre:
    """Construit la classe du pokémon Bulbizarre avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Bulbizarre"
        self.stats = [45, 49, 49, 65, 65, 45]
        self.type = ["plante, poison"]
        self.faiblesse = ["feu", "glace", "vol", "psy"]
        self.capacites = [Capacite("Charge", "normal", 35, 95, 1, 1, "attaque", None, 6), Capacite("Rugissement", "normal", 2/3, 100,1,1, "non-attaque", "attaque", 6)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/bulbizarre.png")
        
class Pikachu:
    """Construit la classe du pokémon Pikachu avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Pikachu"
        self.stats = [35,55,30,50,40,90]
        self.type = ["electrik"]
        self.faiblesse = ["sol"]
        self.capacites = [Capacite("Éclair", "electrik", 40, 100, 2, 1, "attaque", None, 6), Capacite("Rugissement", "normal", 2/3, 100,1,1, "non-attaque", "attaque", 6)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/pikachu.png")
        
class Caninos:
    """Construit la classe du pokémon Caninos avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Caninos"
        self.stats = [55,70,45,70,50,60]
        self.type = ["feu"]
        self.faiblesse = ["eau", "sol", "roche"]
        self.capacites = [Capacite("Morsure", "normal", 60, 100, 1, 1, "attaque", None, 6)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/caninos.png")
        
class Evoli:
    """Construit la classe du pokémon Evoli avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Évoli"
        self.stats = [55, 55, 50, 45, 65, 55]
        self.type = ["normal"]
        self.faiblesse = ["combat"]
        self.capacites = [Capacite("Charge", "normal", 35, 95, 1, 1, "attaque", None, 6), Capacite("Rugissement", "normal", 2/3, 100,1,1, "non-attaque", "attaque", 6)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/evoli.png")

class Mewtwo:
    """Construit la classe du pokémon Mewtwo avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self):
        self.nom = "Mewtwo"
        self.stats = [106, 110, 90, 154, 90, 130]
        self.type = ["psy"]
        self.faiblesse = ["insecte", "spectre", "tenebre"]
        self.capacites = [Capacite("Choc Mental", "psy", 50, 100, 1, 1, "attaque", None, 6), Capacite("Météores", "normal", 60, 100, 1, 1, "attaque", None, 6)]
        self.niveau = 50
        self.image = pygame.image.load("sprite/rfvf/mewtwo.png")