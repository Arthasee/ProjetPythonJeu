"""Fichier avec les différentes Classes du jeu (Pokémon, Capacité)
    """
import random
import pygame
import constante as cst


class Pokemon:
    """Construit un pokémon spécifique avec sa position, ses statistiques, 
    ses capacités et son niveau
    """

    def __init__(self, team, x, y):
        self.team = team
        self.x = x
        self.y = y
        self.__pv_max = None
        self.pv = None
        self.attaque = None
        self.defense = None
        self.att_spe = None
        self.def_spe = None
        self.vitesse = None
        self.nerfs = {
            "attaque": 0,
            "defense": 0,
            "vitesse": 0,
            "attaque_spé": 0,
            "defense_spé": 0
        }
        self.niveau = None
        self.type = None
        self.faiblesse = []
        self.capacites = []
        self.has_attacked = False  # Indicateur pour suivre si le Pokémon a attaqué ce tour
        self.movement_points_used = 0 # Nombre de points de mouvement utilisés ce tour (permet eviter les déplacements trop longs)
        self.is_selected = False
        self.image = None
        
    @property
    def pv_max(self):
        return self.__pv_max

    @pv_max.setter
    def pv_max(self, pv):
        self.__pv_max = pv

    def move(self, dx, dy):
        """Déplace l'unité de dx, dy."""
        if 0 <= self.x + dx < cst.GRID_WIDTH and 0 <= self.y + dy < cst.GRID_HEIGHT:
            self.x += dx
            self.y += dy

    def draw(self, screen):
        """Affiche l'unité sur l'écran."""
        # color = BLUE if self.team == 'player' else RED
        if self.is_selected:
            pygame.draw.rect(screen, cst.GREEN, (self.x * cst.CELL_SIZE,self.y * cst.CELL_SIZE, cst.CELL_SIZE, cst.CELL_SIZE),2)
        screen.blit(self.image, (self.x*cst.CELL_SIZE,self.y*cst.CELL_SIZE))

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
        self.sprite = pygame.image.load("sprite/explosion.png")

class Salameche(Pokemon):
    """Construit la classe du pokémon Salamèche avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self, team, x, y):
        Pokemon.__init__(self, team, x, y)
        self.nom = "Salameche"
        self.pv_max = 39
        self.pv = 39
        self.attaque = 52
        self.defense = 43
        self.att_spe = 60
        self.def_spe = 50
        self.vitesse = 65
        self.type = ["feu"]
        self.faiblesse = ["eau", "sol", "roche"]
        self.capacites = [Capacite("Griffe", "normal", 40, 100,1,1,"attaque", None, 6), Capacite("Rugissement", "normal", 2/3, 100,3,1, "non-attaque", "attaque", 4)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/salameche.png")
        self.image = pygame.transform.scale(self.image, (cst.CELL_SIZE, cst.CELL_SIZE)) # Redimensionner les sprites


class Carapuce(Pokemon):
    """Construit la classe du pokémon Carapuce avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self, team, x, y):
        Pokemon.__init__(self, team, x, y)
        self.nom = "Carapuce"
        self.pv_max = 44
        self.pv = 44
        self.attaque = 48
        self.defense = 65
        self.att_spe = 50
        self.def_spe = 64
        self.vitesse = 43
        self.type = ["eau"]
        self.faiblesse = ["plante", "electrik"]
        self.capacites = [Capacite("Charge", "normal", 35, 95, 1, 1, "attaque", None, 6), Capacite("Mimi-Queue", "normal", 2/3, 100, 3, 1, "non-attaque", "defense", 4)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/carapuce.png")
        self.image = pygame.transform.scale(self.image, (cst.CELL_SIZE, cst.CELL_SIZE)) # Redimensionner les sprites


class Bulbizarre(Pokemon):
    """Construit la classe du pokémon Bulbizarre avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self, team, x, y):
        Pokemon.__init__(self, team, x, y)
        self.nom = "Bulbizarre"
        self.pv_max = 44
        self.pv = 44
        self.attaque = 49
        self.defense = 49
        self.att_spe = 65
        self.def_spe = 65
        self.vitesse = 45
        self.type = ["plante, poison"]
        self.faiblesse = ["feu", "glace", "vol", "psy"]
        self.capacites = [Capacite("Charge", "normal", 35, 95, 1, 1, "attaque", None, 6), Capacite("Rugissement", "normal", 2/3, 100,3,1, "non-attaque", "attaque", 4)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/bulbizarre.png")
        self.image = pygame.transform.scale(self.image, (cst.CELL_SIZE, cst.CELL_SIZE)) # Redimensionner les sprites

class Pikachu(Pokemon):
    """Construit la classe du pokémon Pikachu avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self, team, x, y):
        Pokemon.__init__(self, team, x, y)
        self.nom = "Pikachu"
        self.pv_max = 35
        self.pv = 35
        self.attaque = 55
        self.defense = 30
        self.att_spe = 50
        self.def_spe = 40
        self.vitesse = 90
        self.type = ["electrik"]
        self.faiblesse = ["sol"]
        self.capacites = [Capacite("Eclair", "electrik", 40, 100, 2, 1, "attaque", None, 6), Capacite("Rugissement", "normal", 2/3, 100,3,1, "non-attaque", "attaque", 4)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/pikachu.png")
        self.image = pygame.transform.scale(self.image, (cst.CELL_SIZE, cst.CELL_SIZE)) # Redimensionner les sprites

class Caninos(Pokemon):
    """Construit la classe du pokémon Caninos avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self, team, x, y):
        Pokemon.__init__(self, team, x, y)
        self.nom = "Caninos"
        self.pv_max = 55
        self.pv = 55
        self.attaque = 70
        self.defense = 45
        self.att_spe = 70
        self.def_spe = 50
        self.vitesse = 60
        self.type = ["feu"]
        self.faiblesse = ["eau", "sol", "roche"]
        self.capacites = [Capacite("Morsure", "normal", 60, 100, 1, 1, "attaque", None, 6)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/caninos.png")
        self.image = pygame.transform.scale(self.image, (cst.CELL_SIZE, cst.CELL_SIZE)) # Redimensionner les sprites

class Evoli(Pokemon):
    """Construit la classe du pokémon Evoli avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self, team, x, y):
        Pokemon.__init__(self, team, x, y)
        self.nom = "Evoli"
        self.pv_max = 55
        self.pv = 55
        self.attaque = 55
        self.defense = 50
        self.att_spe = 45
        self.def_spe = 65
        self.vitesse = 55
        self.type = ["normal"]
        self.faiblesse = ["combat"]
        self.capacites = [Capacite("Charge", "normal", 35, 95, 1, 1, "attaque", None, 6), Capacite("Rugissement", "normal", 2/3, 100,3,1, "non-attaque", "attaque", 4)]
        self.niveau = 1
        self.image = pygame.image.load("sprite/rfvf/evoli.png")
        self.image = pygame.transform.scale(self.image, (cst.CELL_SIZE, cst.CELL_SIZE)) # Redimensionner les sprites

class Mewtwo(Pokemon):
    """Construit la classe du pokémon Mewtwo avec ses statistiques, force, faiblesse et capacité
    """
    def __init__(self, team, x ,y):
        Pokemon.__init__(self, team, x, y)
        self.nom = "Mewtwo"
        self.stats = [106, 110, 90, 154, 90, 130]
        self.pv_max = 106
        self.pv = 106
        self.attaque = 110
        self.defense = 90
        self.att_spe = 154
        self.def_spe = 90
        self.vitesse = 130
        self.type = ["psy"]
        self.faiblesse = ["insecte", "spectre", "tenebre"]
        self.capacites = [Capacite("Choc Mental", "psy", 50, 100, 5, 1, "attaque", None, 6), Capacite("Meteores", "normal", 60, 100, 1, 1, "attaque", None, 8)]
        self.niveau = 50
        self.image = pygame.image.load("sprite/rfvf/mewtwo.png")
        self.image = pygame.transform.scale(self.image, (cst.CELL_SIZE, cst.CELL_SIZE)) # Redimensionner les sprites

