import random

class EnemyAI: 
    def __init__(self, Niveau):
        self.difficulty = Niveau   # le niveau va etre choisi au debut du jeu      'facile',  'moyen' ,  ou 'difficile'

    def calcul_mouvement(self, enemy, target, accessible_positions):  
        if self.Niveau ==  "facile" :   
            return self.random_move(accessible_positions)  # un mouvement aléatoire 
        elif self.Niveau == "moyen": 
            return self.move_avec_erreur(enemy, target, error_rate=0.25) # un mouvement en faisant des erreures  jai pris 25%    
        elif self.Niveau == "difficile":
            return self.optimal_move(enemy, target)   # un mouvement optimal

    def random_move(self, accessible_positions):
        """Choisir une position aléatoire parmi celles accessibles."""
        if accessible_positions: 
            return random.choice(accessible_positions)
        return None   

    def move_avec_erreur(self, enemy, target, error_rate):
        """Déplacer vers la cible avec une marge d'erreur."""
        dx, dy = self.get_direction(enemy, target) # on récupere dx et dy mais si on veut introduire une erreur on les modifies 
        if random.random() < error_rate: # on genenre un nombre entre 0 et 1 on le compare a la probabilté  q'une erreur va se generer 
            # Introduire une erreur
            dx, dy = random.choice([(-1, 0), (1, 0), (0, -1), (0, 1)])
        return enemy.x + dx, enemy.y + dy

    def optimal_move(self, enemy, target):
        """Se déplacer directement vers la cible."""
        dx, dy = self.get_direction(enemy, target)
        return enemy.x + dx, enemy.y + dy

    def get_direction(self, enemy, target):
        """Calculer la direction pour se rapprocher de la cible."""
        dx = 1 if enemy.x < target.x else -1 if enemy.x > target.x else 0
        dy = 1 if enemy.y < target.y else -1 if enemy.y > target.y else 0
        return dx, dy
