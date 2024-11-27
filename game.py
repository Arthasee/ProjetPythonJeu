"""Fichier du jeu principal
    """
import random
import pygame
from maps import Map 
from screen import Screen 
from unit import *


class Game:
    """
    Classe pour représenter le jeu.

    ...
    Attributs
    ---------
    screen: pygame.Surface
        La surface de la fenêtre du jeu.
    player_units : list[Unit]
        La liste des unités du joueur.
    enemy_units : list[Unit]
        La liste des unités de l'adversaire.
    """

    def __init__(self, screen):
        """
        Construit le jeu avec la surface de la fenêtre.

        Paramètres
        ----------
        screen : pygame.Surface
            La surface de la fenêtre du jeu.
        """
        self.screen = pygame.display.set_mode((MAP_WIDTH+ATH_WIDTH,TOTAL_HEIGHT)) # Taille écran
        self.clock = pygame.time.Clock() # Implémentation d'un tracker de temps
        # Instanciation de la carte
        self.maps = Map(self.screen)
        # pygame.mixer.init()
        # pygame.mixer.music.load("music/1-03. Title Screen.mp3")
        # pygame.mixer.music.play()

        self.current_turn = 'player' # Commence par le tour du joueur

        # self.player_units = [Unit(0, 0, 10, 2, 'player'),
        #                      Unit(1, 0, 10, 2, 'player')]

        # self.enemy_units = [Unit(6, 6, 8, 1, 'enemy'),
        #                     Unit(7, 6, 8, 1, 'enemy')]

        self.player_units = [Pokemon(Bulbizarre(),'player', 0, 0)]
        self.enemy_units = [Pokemon(Carapuce(), 'enemy', 47, 39)]        

    def get_accessible_positions(self, unit, max_distance): # Permet d'obtenir les positions accessibles par le joueur où l'IA à partir de la position actuelle.
        accessible_positions = []
        start_x, start_y = unit.x, unit.y

        for dx in range(-max_distance, max_distance + 1):
            for dy in range(-max_distance, max_distance + 1):
                if abs(dx) + abs(dy) <= max_distance:
                    new_x, new_y = start_x + dx, start_y + dy
                    if 0 <= new_x < GRID_WIDTH and 0 <= new_y < GRID_HEIGHT:  # S'assurer que les positions sont dans la grille
                        accessible_positions.append((new_x, new_y))

        return accessible_positions
    
    def highlight_positions(self, positions, color, alpha=178): # Permet la coloration des cases de potentiels déplacements lors du tour
        # Créer une surface avec transparence
        highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        r, g, b = color
        highlight_surface.fill((r, g, b, alpha))  # Remplir avec la couleur et l'opacité

        for x, y in positions:
            self.screen.blit(highlight_surface, (x * CELL_SIZE, y * CELL_SIZE))

    def handle_player_turn(self):
        """Tour du joueur"""
        self.player_action_points = 10  # Réinitialise les points d'actions (PA) au début du tour
        selected_unit = None # Tant que l'unité n'est pas sélectionnée
        initial_position = None  # Pour enregistrer la position initiale du tour
        accessible_positions = []  # Pour garder la zone de déplacement fixe

        while True:  # Permet de continuer le tour jusqu'à ce que le joueur termine manuellement

            # Calculer les positions accessibles si un pion est sélectionné
            if selected_unit and not accessible_positions:
                accessible_positions = self.get_accessible_positions(selected_unit, MAX_DISTANCE)

            # Rafraîchir l'affichage avec les surlignages
            self.flip_display(highlight_positions=accessible_positions, highlight_color=(135, 206, 235))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Clic gauche
                        mouse_x, mouse_y = event.pos
                        grid_x = mouse_x // CELL_SIZE
                        grid_y = mouse_y // CELL_SIZE

                        # Vérifier si on a cliqué sur un pion du joueur
                        if not selected_unit:
                            for unit in self.player_units:
                                if unit.x == grid_x and unit.y == grid_y:
                                    selected_unit = unit
                                    selected_unit.is_selected = True
                                    # Enregistrer la position initiale du tour
                                    initial_position = (selected_unit.x, selected_unit.y)
                                    # Calculer les positions accessibles une seule fois
                                    accessible_positions = self.get_accessible_positions(selected_unit, MAX_DISTANCE)
                                    break

                        # Si une unité est déjà sélectionnée, vérifier le déplacement
                        elif selected_unit and (grid_x, grid_y) in accessible_positions:
                            # Calculer la distance parcourue à partir de la position initiale
                            distance_from_initial = abs(grid_x - initial_position[0]) + abs(grid_y - initial_position[1])

                            # Vérifier si le joueur a suffisamment de PA pour effectuer ce déplacement
                            if distance_from_initial <= 10:
                                # Mettre à jour la position de l'unité
                                selected_unit.x = grid_x
                                selected_unit.y = grid_y

                                # Mettre à jour les points d'action en fonction de la distance parcourue depuis la position initiale
                                self.player_action_points = 10 - distance_from_initial

                                # Rafraîchir l'affichage après déplacement
                                self.flip_display(highlight_positions=accessible_positions, highlight_color=(135, 206, 235))
                                pygame.display.flip()

                    # Vérifier si on a cliqué sur le bouton de fin du tour
                    if event.button == 1 and self.end_turn_button_rect.collidepoint(event.pos):
                        # Fin du tour
                        if selected_unit:
                            selected_unit.is_selected = False
                        self.current_turn = 'enemy'
                        return

                # Retour à la position initiale avec clic droit ou `Backspace`
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Clique droit pour annuler
                    if selected_unit and initial_position:
                        selected_unit.x, selected_unit.y = initial_position  # Restaurer la position initiale
                        self.player_action_points = 10  # Restaurer tous les PA utilisés
                        accessible_positions = self.get_accessible_positions(selected_unit, MAX_DISTANCE)
                        self.flip_display(highlight_positions=accessible_positions, highlight_color=(135, 206, 235))
                        pygame.display.flip()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:  # Retour avec Backspace
                    if selected_unit and initial_position:
                        selected_unit.x, selected_unit.y = initial_position  # Restaurer la position initiale
                        self.player_action_points = 10  # Restaurer tous les PA utilisés
                        accessible_positions = self.get_accessible_positions(selected_unit, MAX_DISTANCE)
                        self.flip_display(highlight_positions=accessible_positions, highlight_color=(135, 206, 235))
                        pygame.display.flip()

    def handle_enemy_turn(self):
        """IA très simple pour les ennemis."""
        self.enemy_action_points = 10 # PA de l'adversaire
        for enemy in self.enemy_units:
            # Déplacement aléatoire
            target = random.choice(self.player_units)
            # Calculer les positions accessibles et les colorer en rouge pour donner une indication au joueur, les déplacements possibles de l'IA
            accessible_positions = self.get_accessible_positions(enemy, MAX_DISTANCE)
            self.flip_display(highlight_positions=accessible_positions, highlight_color=(255,182,193))            
            original_position = (enemy.x, enemy.y)

            while self.enemy_action_points > 0:
                if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                    # Attaque si à portée
                    enemy.attaquer(enemy.capacites[0],target)
                    self.enemy_action_points -= 1

                    # Vérifier si le joueur est éliminé
                    if target.pv <= 0:
                        print("Le joueur a été vaincu")
                        pygame.quit()
                        exit()
                    # Fin du tour de l'IA après l'attaque
                    break

                dx,dy = 0, 0
                if enemy.x < target.x :
                    dx = 1 # déplacement vers la droite pour venir vers le joueur
                elif enemy.x > target.x :
                    dx = -1 # déplacement vers la gauche pour venir vers le joueur
                
                if enemy.y < target.y :
                    dy = 1 # déplacement vers le bas pour venir vers le joueur
                elif enemy.y > target.y :
                    dy = -1 # déplacement vers le haut pour venir vers le joueur

                new_x = enemy.x + dx
                new_y = enemy.y + dy
                total_distance = abs(new_x - original_position[0]) + abs(new_y - original_position[1])

                if total_distance <= MAX_DISTANCE: # Permet de respecter le nombre de case limite de déplacement
                    if dx != 0 and dy != 0 :
                        if random.choice([True, False]):
                            dy = 0
                        else :
                            dx = 0
                    previous_position = (enemy.x, enemy.y)
                    enemy.move(dx, dy)

                    if (enemy.x, enemy.y) != previous_position:
                        self.enemy_action_points -= 1

                    self.flip_display(highlight_positions=accessible_positions, highlight_color=(255,182,193))
                    self.clock.tick(5) # Vitesse raisonnable pour voir l'IA jouer
                else :
                    break

            # Attaque si possible
            if abs(enemy.x - target.x) <= 1 and abs(enemy.y - target.y) <= 1:
                enemy.attaquer(enemy.capacites[0] ,target)
                if target.pv <= 0:
                    self.player_units.remove(target)
        self.current_turn = 'player'

    def flip_display(self, highlight_positions=None, highlight_color=None):
        """Affiche le jeu."""
        # Dessiner l'arrière-plan (carte)
        self.maps.update()

        # Affiche la grille in game
        for x in range(0, MAP_WIDTH, CELL_SIZE):
            for y in range(0, TOTAL_HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(self.screen, WHITE, rect, 1)

        # Surligner les positions accessibles si fournies
        if highlight_positions and highlight_color:
            self.highlight_positions(highlight_positions, highlight_color)

        # Affiche les unités par-dessus les surlignages
        for unit in self.player_units + self.enemy_units:
            Pokemon.draw(unit,self.screen)
        
        self.draw_ath()  # Dessiner l'ATH

        # Rafraîchit l'écran
        pygame.display.flip()

    def draw_ath(self):
        """Dessine l'ATH sur le côté droit"""
        ath_rect = pygame.Rect(MAP_WIDTH,0,ATH_WIDTH,TOTAL_HEIGHT) # Zone de l'ATH
        pygame.draw.rect(self.screen,(50,50,50),ath_rect) # Fond gris foncé de l'ath droit
        font = pygame.font.Font(None,36)
        text_turn = font.render(f"Tour : {self.current_turn.capitalize()}", True, WHITE)
        self.screen.blit(text_turn, (MAP_WIDTH + 10, 20))

        # Afficher PA restant
        if self.current_turn == 'player' :
            pa_text = font.render(f"PA Restants : {self.player_action_points}",True, WHITE)
        else :
            pa_text = font.render(f"PA Restants : {self.enemy_action_points}", True, WHITE)
        self.screen.blit(pa_text, (MAP_WIDTH+10,60))

        # Dessiner le bouton "Fin du tour"
        self.end_turn_button_rect = pygame.Rect(MAP_WIDTH + 30, TOTAL_HEIGHT - 80, 140, 50)  # Dimensions du bouton
        pygame.draw.rect(self.screen, (0, 255, 0), self.end_turn_button_rect)  # Carré vert

        # Ajouter le texte "Fin du tour" sur le bouton
        end_turn_text = font.render("Fin du tour", True, BLACK)
        text_rect = end_turn_text.get_rect(center=self.end_turn_button_rect.center)
        self.screen.blit(end_turn_text, text_rect)

    def run(self):
        """Boucle running du jeu."""
        running = True
        while running:
            # Gérer les événements
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Ajouter une vérification globale pour chaque événement capturé (test input)
                print(f"Événement capturé : {event}")

            # Rafraîchir l'affichage
            self.flip_display()
            pygame.display.flip()

            # Limiter la boucle à 30 FPS
            self.clock.tick(30)


def main():
    """Fonction principal
    """
    # Initialisation de Pygame
    pygame.init()

    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    pygame.display.set_caption("Mon jeu de stratégie")

    # Instanciation du jeu
    game = Game(screen)

    # Boucle principale du jeu
    while True:
        game.handle_player_turn()
        game.handle_enemy_turn()

if __name__ == "__main__":
    main()
