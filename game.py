"""Fichier du jeu principal
    """
import random
import pygame
import pygame_menu
from constante import *
from maps import Map 
from screen import Screen 
from unit import *
from pathfinding import Chemin
from interface import Interface
from menus import Menu

surface = pygame.display.set_mode((600, 400))

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

    def __init__(self, screen, player, enemy, carte, difficulty="normal"):
        """
        Construit le jeu avec la surface de la fenêtre.

        Paramètres
        ----------
        screen : pygame.Surface
            La surface de la fenêtre du jeu.
        """
        self.screen = pygame.display.set_mode((MAP_WIDTH+ATH_WIDTH,TOTAL_HEIGHT)) # Taille écran
        self.clock = pygame.time.Clock() # Implémentation d'un tracker de temps
        self.maps = Map(self.screen, carte) # Instanciation de la carte
        self.difficulty = difficulty
        self.chemin = Chemin(self)  # Instanciation de l'objet Chemin
        self.interface = Interface(self) # Instanciation de l'objet Interface
        self.menu = Menu(self)  # Instanciation de l'objet Menu

        pygame.mixer.init()
        pygame.mixer.music.load("music/battle.mp3")
        pygame.mixer.music.set_volume(0.04)
        pygame.mixer.music.play()

        self.current_turn = 'player' # Commence par le tour du joueur
        self.player_units = player
        self.enemy_units = enemy
        self.selected_unit = self.player_units[0] if self.player_units else None # Unité sélectionnée par défaut
        self.nerfed_units = []  # Contient les Pokémon ayant reçu des nerfs
        self.selected_attack = None
        self.interface.initialize_messages() # Initialisation des messages d'information
        self.menu.current_menu = "main" # Menu de sélection principal en jeu
        self.accessible_positions = [] # Positions accessibles pour le déplacement
        self.highlighted_target = None # Position surlignée temporairement

        # Initialisation des rectangles pour les boutons d'action de l'ATH (interface utilisateur)
        self.attack_button_rect = pygame.Rect(MAP_WIDTH + ATH_WIDTH // 2 - button_width - padding // 2, 100, button_width, button_height)
        self.move_button_rect = pygame.Rect(MAP_WIDTH + ATH_WIDTH // 2 - button_width - padding // 2, 100 + button_height + padding, button_width, button_height)
        self.pokemon_button_rect = pygame.Rect(self.attack_button_rect.right + padding, 100, button_width, button_height)  # À droite du bouton Attaquer
        self.pass_turn_button_rect = pygame.Rect(self.move_button_rect.right + padding, 100 + button_height + padding, button_width, button_height)  # À droite du bouton Déplacer
        self.back_button_rect = pygame.Rect(MAP_WIDTH + ATH_WIDTH // 2 - 100, 400, 200, 50)  # Bouton centré pour "Retour"

    def handle_player_turn(self):
        """Tour du joueur"""
        print("Début du tour du joueur") #Debug
        self.player_action_points = 25  # Réinitialise les points d'actions au début du tour
        # Réinitialiser les PA de déplacement pour tous les Pokémon
        for pokemon in self.player_units:
            pokemon.movement_points_used = 0 # Remet à zéro les points de mouvement utilisés
            pokemon.has_attacked = False # Réinitialise l'état d'attaque
        if not self.selected_unit and self.player_units: # Si pas d'unité sélectionnée et qu'il y a des unités jouables
            self.info_message = "Unité sélectionnée par défaut : {}".format(self.player_units[0].nom)
            self.selected_unit = self.player_units[0] # Sélectionner la première unité jouable par défaut

        try:
             # Boucle principale du tour du joueur
            while True:  # Permet de continuer le tour jusqu'à ce que le joueur termine manuellement
                # Rafraîchir l'affichage avec les surlignages
                if self.menu.current_menu == "move":
                    self.flip_display(highlight_positions=self.accessible_positions, highlight_color=(135, 206, 235))
                else:
                    self.flip_display()
                pygame.display.flip()
                # Gestion des événements (clics, survols, etc.)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_x, mouse_y = event.pos
                        buttons = self.menu.get_menu_buttons()
                        # Si le joueur est dans le menu principal, configure les boutons correspondants
                        if self.menu.current_menu == "main":
                            buttons = [
                                ("Attaquer", self.attack_button_rect, lambda: self.start_attack_action()),
                                ("Deplacer", self.move_button_rect, lambda: self.start_move_action()),
                                ("Pokemon", self.pokemon_button_rect, lambda: self.menu.select_pokemon_action()),
                                ("Passer le tour", self.pass_turn_button_rect, lambda: self.end_turn_and_exit())
                            ]
                        # Si le joueur est dans le menu des compétences, configure les boutons correspondants
                        elif self.menu.current_menu == "skills" and self.selected_unit:
                            buttons = [
                                (skill.nom, rect, lambda skill=skill: self.use_skill(skill))
                                for skill, rect in zip(self.selected_unit.capacites, [self.attack_button_rect, self.move_button_rect, self.pokemon_button_rect, self.pass_turn_button_rect])
                            ]
                            buttons.append(("Retour", self.back_button_rect, lambda: self.menu.switch_to_menu("main")))
                        # Si le joueur est dans le menu de déplacement
                        elif self.menu.current_menu == "move":
                            buttons = [
                                ("Valider", self.attack_button_rect, lambda: self.confirm_move()),
                                ("Annuler", self.move_button_rect, lambda: self.cancel_move()),
                                ("Retour", self.back_button_rect, lambda: self.menu.switch_to_menu("main"))
                            ]
                        # Si le joueur est dans le menu de sélection de cible
                        elif self.menu.current_menu == "target":
                            # Ajout de la logique de sélection de cible lorsque le menu actuel est "target"
                            targets = self.get_available_targets()
                            buttons = [
                                (target.nom, self.menu.get_pokemon_button_rect(i), lambda target=target: self.attack_target(target))
                                for i, target in enumerate(targets)
                            ]
                            buttons.append(("Retour", self.menu.calculate_back_button_position(len(buttons)), lambda: self.menu.switch_to_menu("skills")))

                        # Méthode pour gérer les clics sur le menu
                        self.menu.handle_click_on_menu(buttons, mouse_x, mouse_y)

                        # Gestion du déplacement temporaire après clic sur une case
                        if self.selected_unit and (self.menu.current_menu == "move"):
                            grid_x = mouse_x // CELL_SIZE
                            grid_y = mouse_y // CELL_SIZE
                            if (grid_x, grid_y) in self.accessible_positions:  # Vérifie si la case est accessible
                                if not self.check_collision(grid_x, grid_y) and not self.is_occupied(grid_x, grid_y):
                                    # Déplacement temporairement de l'unité
                                    self.highlighted_target = (grid_x, grid_y)  # Stocker la position surlignée
                                    # Calcul du coût en points d'action
                                    current_x, current_y = self.selected_unit.x, self.selected_unit.y
                                    distance = abs(current_x - grid_x) + abs(current_y - grid_y)
                                    cost_message = f"Ce déplacement coutera {distance} points d'action."
                                    self.interface.set_info_message(cost_message)
                                    self.flip_display()  # Rafraîchir l'affichage pour inclure la nouvelle case surlignée
                                    pygame.display.flip()

                    # Survol des compétences avec la souris pour afficher le nom de la compétence
                    if event.type == pygame.MOUSEMOTION and self.menu.current_menu == "skills" and self.selected_unit:
                        mouse_x, mouse_y = event.pos
                        for skill, rect in zip(self.selected_unit.capacites, [self.attack_button_rect, self.move_button_rect, self.pokemon_button_rect, self.pass_turn_button_rect]):
                            if rect.collidepoint(mouse_x, mouse_y):
                                cost_message = f"Utiliser {skill.nom} coutera {skill.cout_pa} points d'action."
                                self.interface.set_info_message(cost_message)
                                break
                        else:
                            self.interface.set_info_message("") # Si la souris n'est sur aucune compétence, on réinitialise le message

                self.interface.draw_ath() # Dessiner l'ATH à chaque itération
                
        except StopIteration:
            print("Tour du joueur terminé, passant au tour de l'ennemi") #Debug
            pass # Sortir de la boucle proprement lorsque le tour se termine

    def handle_enemy_turn(self):
        """IA qui effectue des déplacements et des attaques."""
        self.enemy_action_points = 25 # Réinitialise les points d'actions (PA) au début du tour pour l'IA
        # Réinitialiser l'état des Pokémon ennemis (points de mouvement et attaques)
        for enemy in self.enemy_units:
            enemy.movement_points_used = 0
            enemy.has_attacked = False

            if not self.player_units:
                print("Tous les Pokémon du joueur sont vaincus.") #Debug
                pygame.quit()
                exit()

            # Choisir une cible en fonction de la difficulté
            target = self.choose_target(enemy)
            if not target:
                print(f"{enemy.nom} n'a pas trouvé de cible.") #Debug
                continue

            while self.enemy_action_points > 0:
                print(f"Points d'action restants pour {enemy.nom} : {self.enemy_action_points}") #Debug
                # Vérifier si l'ennemi peut se déplacer
                max_movement_points = min(10 - enemy.movement_points_used, self.enemy_action_points)
                if max_movement_points <= 0:
                    print(f"{enemy.nom} ne peut plus se déplacer.") #Debug
                    break
                # Récupère les positions accessibles en fonction des points de mouvement
                accessible_positions = self.get_accessible_positions(enemy, max_distance=max_movement_points)
                if accessible_positions:
                    # Se déplacer vers la cible
                    target_position = min(accessible_positions, key=lambda pos: abs(pos[0] - target.x) + abs(pos[1] - target.y))
                    path = self.chemin.calculate_path(enemy.x, enemy.y, target_position[0], target_position[1], enemy.type)
                    # Si aucun chemin valide n'est trouvé, l'ennemi reste sur place
                    if not path:
                        print(f"{enemy.nom} ne peut pas atteindre la cible.")  #Debug
                        break
                    # Parcourir le chemin pour déplacer l'ennemi
                    for (x, y) in path:
                        if enemy.movement_points_used >= 10 or self.enemy_action_points <= 0:
                            break
                        if (x, y) in accessible_positions and not self.check_collision(x, y) and not self.is_occupied(x, y):
                            enemy.x, enemy.y = x, y
                            self.flip_display()
                            pygame.display.flip()
                            self.clock.tick(5) # Contrôler la vitesse de l'animation de déplacement de l'IA
                            enemy.movement_points_used += 1
                            self.enemy_action_points -= 1

                # Vérifier si l'ennemi peut attaquer
                if self.attempt_attack(enemy, target):
                    print(f"{enemy.nom} attaque {target.nom} à ({target.x}, {target.y}).") #Debug
                    break

                # Si aucune action n'est possible
                if not accessible_positions:
                    print(f"{enemy.nom} n'a plus d'actions disponibles.") #Debug
                    break

            print(f"{enemy.nom} a terminé son tour.") #Debug
        # Passer au tour du joueur après avoir terminé toutes les actions ennemies
        self.current_turn = 'player'
        self.player_action_points = 25

    def end_turn(self):
        """Termine le tour du joueur et passe au tour de l'ennemi."""
        # Désélectionner l'unité actuellement sélectionnée
        if self.selected_unit:
            self.selected_unit.is_selected = False
        self.selected_unit = None  # Aucune unité n'est sélectionnée après la fin du tour
        self.menu.current_menu = "main"
        self.player_action_points = 0
        self.accessible_positions = []

        # Vérifier si tous les Pokémon ennemis ont été vaincus
        if not self.enemy_units:
            pygame.quit()
            exit()
        print(f"Fin du tour (end_turn): {self.current_turn}") #Debug
        self.current_turn = 'enemy' if self.current_turn == 'player' else 'player'
        print(f"Nouveau tour : {self.current_turn}") #Debug
        self.interface.draw_ath()
        self.flip_display()
        pygame.display.flip()
        
    def end_turn_and_exit(self):
        """Termine le tour du joueur et sort de la boucle de gestion du tour."""
        print("Fin du tour du joueur via end_turn_and_exit")
        self.end_turn()
        raise StopIteration  # Utiliser une exception pour sortir de la boucle while dans handle_player_turn

    def get_accessible_positions(self, unit, max_distance):
        positions = set()  # Stocker les positions accessibles dans un ensemble
        queue = [(unit.x, unit.y, 0)]  # File d'attente pour BFS (x, y, distance)
        visited = set()  # Conserver les positions visitées pour éviter les répétitions

        while queue:
            x, y, distance = queue.pop(0)  # Extraire la position actuelle et la distance parcourue

            if (x, y) in visited:
                continue

            visited.add((x, y))

            # Vérifier si la case est accessible (ne doit pas être occupée par un autre Pokémon et ne doit pas y avoir de collision)
            if distance <= max_distance and not self.is_occupied(x, y) and not self.check_collision(x, y):
                path = self.chemin.calculate_path(unit.x, unit.y, x, y, unit.type)
                if len(path) - 1 <= max_distance:  # Vérifier que le chemin réel respecte les points d'action disponibles
                    positions.add((x, y))
            # Ajouter les cases adjacentes à la file d'attente + Vérification type de cases
            if distance < max_distance:
                neighbors = self.chemin.get_neighbors(x, y, unit.type)
                for nx, ny in neighbors:
                    queue.append((nx, ny, distance + 1))

        # Exclure la position actuelle de l'unité
        positions.discard((unit.x, unit.y))

        return positions

    def flip_display(self, highlight_positions=None, highlight_color=None):
        """Affiche le jeu."""
        # Dessiner l'arrière-plan (carte)
        self.maps.update()
        
        # Crée une surface transparente
        grid_surface = pygame.Surface((MAP_WIDTH, TOTAL_HEIGHT), pygame.SRCALPHA)
        # Couleur avec transparence (RGBA) : blanc avec 50% d'opacité
        TRANSPARENT_WHITE = (255, 255, 255, 128)

        # Affiche la grille in game
        for x in range(0, MAP_WIDTH, CELL_SIZE):
            for y in range(0, TOTAL_HEIGHT, CELL_SIZE):
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(grid_surface, TRANSPARENT_WHITE, rect, 1)

        # Surligner les positions accessibles
        if highlight_positions and highlight_color:
            self.interface.highlight_positions(highlight_positions, highlight_color)

        # Surligner la position temporaire sélectionnée (en vert)
        if self.highlighted_target:
            self.interface.highlight_positions([self.highlighted_target], (0, 255, 0), alpha=150)

        # Affiche les unités par-dessus les surlignages
        for unit in self.player_units + self.enemy_units:
            Pokemon.draw(unit,self.screen)
        
        self.interface.draw_ath()
        pygame.display.flip()

    def check_collision(self, grid_x, grid_y):
        """Vérifie si une case de la grille entre en collision avec un obstacle."""
        pixel_x = grid_x * CELL_SIZE
        pixel_y = grid_y * CELL_SIZE
        future_rect = pygame.Rect(pixel_x, pixel_y, CELL_SIZE, CELL_SIZE)

        for rect in self.maps.collisions:
            if future_rect.colliderect(rect):
                 
                return True
        return False
    
    def is_occupied(self, x, y):
        """Vérifie si une position donnée est occupée par une unité (joueur ou ennemi)."""
        for unit in self.player_units + self.enemy_units:
            if unit.x == x and unit.y == y:
                return True
        return False

    def start_move_action(self):
        """Initialise l'action de déplacement en calculant les positions accessibles"""
        if not self.selected_unit and self.player_units:
            self.selected_unit = self.player_units[0]
        
        if self.selected_unit:
            self.original_position = (self.selected_unit.x, self.selected_unit.y)

            # Limiter les déplacements à 10 PA moins ceux déjà utilisés
            max_movement_points = 10 - self.selected_unit.movement_points_used
            if max_movement_points <= 0:
                self.interface.set_info_message("Ce Pokemon ne peut plus se déplacer ce tour.")
                return

            max_distance = min(max_movement_points, self.player_action_points)  # Respecter les PA globaux
            self.accessible_positions = self.get_accessible_positions(self.selected_unit, max_distance)
            
            self.menu.current_menu = "move"
            self.flip_display(highlight_positions=self.accessible_positions, highlight_color=(135, 206, 235))
            pygame.display.flip()

    def cancel_move(self):
        """Annule le déplacement de l'unité et revient à la position d'origine."""
        if self.selected_unit:
            if hasattr(self, 'original_position'):
                self.selected_unit.x, self.selected_unit.y = self.original_position
                del self.original_position  # Supprimer la position d'origine après l'annulation

        # Supprimer la position de destination temporaire, s'il y en a une
        self.highlighted_target = None
        self.menu.current_menu = "main"
        self.accessible_positions = [] 

        self.interface.set_info_message("")
        self.flip_display()
        pygame.display.flip()

    def confirm_move(self):
        """Confirme le déplacement de l'unité sélectionnée avec animation."""
        if self.selected_unit and self.highlighted_target:
            start_x, start_y = self.selected_unit.x, self.selected_unit.y
            end_x, end_y = self.highlighted_target
            path = self.chemin.calculate_path(start_x, start_y, end_x, end_y, self.selected_unit.type)

            # Calcul de la distance parcourue
            distance_moved = len(path) - 1

            # Vérification des PA disponibles
            if self.player_action_points >= distance_moved and self.selected_unit.movement_points_used + distance_moved <= 10:
                # Mise à jour des positions et des PA utilisés
                for (x, y) in path:
                    self.selected_unit.x = x
                    self.selected_unit.y = y
                    self.flip_display()  # Mettre à jour l'affichage après chaque déplacement
                    pygame.display.flip()
                    self.clock.tick(5)  # Contrôler la vitesse de l'animation

                self.player_action_points -= distance_moved
                self.selected_unit.movement_points_used += distance_moved

                self.menu.current_menu = "main"
                self.accessible_positions = []
                self.highlighted_target = None
            else:
                self.interface.set_info_message("Pas assez de points d'action pour ce déplacement.")
                self.cancel_move()

            self.flip_display()
            pygame.display.flip()

    def start_attack_action(self):
        """Démarre l'action d'attaque et affiche le menu des compétences."""
        if self.selected_unit:
            self.menu.current_menu = "skills"  
            self.interface.display_message_by_id(0)  
            self.flip_display() 
            pygame.display.flip()

    def use_skill(self, skill):
        """Utiliser la compétence sélectionnée."""
        if not self.selected_unit:
            self.interface.set_info_message("Aucun Pokemon sélectionné.")
            return

        # Vérifier si le Pokémon a déjà attaqué
        if self.selected_unit.has_attacked:
            self.interface.set_info_message(f"{self.selected_unit.nom} a déjà attaqué ce tour.")
            return

        # Vérifier si le joueur a assez de PA pour attaquer
        if self.player_action_points < skill.cout_pa:
            self.interface.display_message_by_id(3)  # Pas assez de points d'action pour attaquer
            return

        # Sélectionner l'attaque
        self.selected_attack = skill

        # Vérifier s'il y a des cibles disponibles à portée
        available_targets = self.get_available_targets()
        if available_targets:
            target_positions = [(target.x, target.y) for target in available_targets]
            self.interface.highlight_positions(target_positions, RED, alpha=100)  # Surlignage rouge pour les ennemis à portée
            self.menu.switch_to_menu("target")
        else:
            self.interface.set_info_message("Aucune cible à portée pour cette attaque.")
            self.menu.switch_to_menu("main")

    def get_available_targets(self):
        """Renvoie une liste des ennemis qui sont à portée de l'attaque sélectionnée."""
        if not self.selected_unit or not self.selected_attack:
            return []

        targets = []
        max_distance = self.selected_attack.distance

        # Parcourir tous les ennemis pour voir s'ils sont à portée de l'attaque sélectionnée
        for enemy in self.enemy_units:
            distance = abs(self.selected_unit.x - enemy.x) + abs(self.selected_unit.y - enemy.y)
            if distance <= max_distance:
                targets.append(enemy)
        
        return targets

    def attack_target(self, target):
        """Utilise l'attaque sélectionnée contre la cible choisie."""
        if self.selected_unit and self.selected_attack:
            if self.player_action_points >= self.selected_attack.cout_pa:
                # Utiliser l'attaque
                self.selected_unit.attaquer(self.selected_attack, target)
                self.interface.set_info_message(f"{self.selected_unit.nom} utilise {self.selected_attack.nom} sur {target.nom} !")

                # Déduire les points d'action nécessaires
                self.player_action_points -= self.selected_attack.cout_pa
                self.selected_unit.has_attacked = True  # Marquer comme ayant attaqué

                # Vérifier si le Pokémon adverse est vaincu
                if target.pv <= 0:
                    self.interface.set_info_message(f"{target.nom} a été vaincu!")
                    self.enemy_units.remove(target)

                    # Vérifier la condition de victoire
                    if not self.enemy_units:
                        pygame.quit()
                        exit()

                # Réinitialiser l'attaque sélectionnée et revenir au menu principal
                self.selected_attack = None
                self.menu.switch_to_menu("main")
            else:
                self.interface.set_info_message("Pas assez de points d'action pour attaquer.")

    def apply_nerf(self, target_pokemon, stat, value=1):
        """Applique un nerf à un Pokémon cible."""
        print(f"Applying nerf: {stat} by {value} to {target_pokemon.nom}") #Debug
        if target_pokemon not in self.nerfed_units:
            self.nerfed_units.append(target_pokemon)
        
        # Ajouter le nerf à la statistique concernée
        if stat in target_pokemon.nerfs:
            target_pokemon.nerfs[stat] += value
        else:
            target_pokemon.nerfs[stat] = value
        self.interface.draw_ath()
        pygame.display.flip()

    def attempt_attack(self, enemy, target):
        distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
        if distance == 1:
            available_skills = [s for s in enemy.capacites if s.cout_pa <= self.enemy_action_points]
            if available_skills:
                skill = random.choice(available_skills)
                enemy.attaquer(skill, target)
                self.enemy_action_points -= skill.cout_pa
                if target.pv <= 0:
                    self.player_units.remove(target)
                return True  # Attaque réussie
        return False  # Pas d'attaque possible

    def choose_target(self, enemy):
        """Choisit une cible en fonction de la difficulté."""
        if self.difficulty == "easy":
            return random.choice(self.player_units)  # Cible aléatoire
        elif self.difficulty == "normal":
            return min(self.player_units, key=lambda p: abs(p.x - enemy.x) + abs(p.y - enemy.y))  # Cible la plus proche
        elif self.difficulty == "hard":
            return min(
                self.player_units,
                key=lambda p: (enemy.type[0] in p.faiblesse, abs(p.x - enemy.x) + abs(p.y - enemy.y))
            )  # Combine faiblesse et proximité
        return None

def generate_random_position(game, min_x=0, max_x=5, min_y=0, max_y=5):
    """
    Génère une position aléatoire entre (min_x, min_y) et (max_x, max_y) qui n'entre pas en collision.
    """
    while True:
        x = random.randint(min_x, max_x)
        y = random.randint(min_y, max_y)
        if not game.check_collision(x, y) and not game.is_occupied(x, y):
            return x, y

def main():
    """Fonction principale"""
    # Initialisation de Pygame
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("music/1-03. Title Screen.mp3")
    pygame.mixer.music.set_volume(0.04)
    pygame.mixer.music.play()

    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    pygame.display.set_caption("PokeBattle")
    menu = pygame_menu.Menu('Welcome', TOTAL_WIDTH, TOTAL_HEIGHT,
                             theme=pygame_menu.themes.THEME_BLUE, position=(50, 50, True))

    # Liste des Pokémon disponibles
    starter_pokemon = [
        ("Salamèche", Salameche('player', 0, 0)), ("Carapuce", Carapuce('player', 0, 0)), ("Pikachu", Pikachu('player', 0, 0)),
        ("Évoli", Evoli('player', 0, 0)), ("Bulbizarre", Bulbizarre('player', 0, 0)), ("Mewtwo", Mewtwo('player', 0, 0)), ("Caninos", Caninos('player', 0, 0))
    ]

    # Ajout de plusieurs sélecteurs pour choisir 3 Pokémon
    selectors = []
    for i in range(3):
        selectors.append(menu.add.selector(
            f'Choix Pokémon {i + 1} :', [(name, j) for j, (name, _) in enumerate(starter_pokemon)]
        ))

    # Zone pour afficher un message d'erreur
    error_label = menu.add.label('', max_char=-1, font_size=24, font_color=RED)

    # Sélection de la carte
    selecteur_carte = menu.add.selector('Carte :', [('Ville', 1), ('Plage', 2), ('Grotte', 3)])

    # Sélection difficulté
    difficulty_selector = menu.add.selector('Difficulté :', [('Facile', 'easy'), ('Normale', 'normal'), ('Difficile', 'hard')])

    
    # Bouton pour sélectionner des Pokémon aléatoires
    def select_random_pokemons(selectors, starter_pokemon):
        random_indices = random.sample(range(len(starter_pokemon)), 3)
        for i, selector in enumerate(selectors):
            selector.set_value(random_indices[i])

    menu.add.button('Sélection Aléatoire', lambda: select_random_pokemons(selectors, starter_pokemon))

    # Bouton pour valider le menu
    def validate_selection():
        selected_indices = [selector.get_value()[0][1] for selector in selectors]
        
        # Vérification des doublons
        if len(set(selected_indices)) < len(selected_indices):
            error_label.set_title("Vous ne pouvez pas sélectionner deux fois le même Pokémon.")
            return
        
        # Tout est valide, fermer le menu
        menu.disable()
    
    menu.add.button('Play', validate_selection)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.mainloop(surface)

    # Extraction des Pokémon sélectionnés
    selected_indices = [selector.get_value()[0][1] for selector in selectors]
    player_team = [starter_pokemon[j][1] for j in selected_indices]

    # Définir les spawns spécifiques selon la carte sélectionnée (gestion eau pour plage)
    choix_map = {1: "map_1.tmx", 2: "map_2.tmx", 3: "map_3.tmx"}[selecteur_carte.get_value()[0][1]]
    if choix_map == "map_2.tmx":  # Carte "plage"
        player_spawn_area = {"min_x": 1, "max_x": 5, "min_y": 10, "max_y": 19}
        enemy_spawn_area = {"min_x": 21, "max_x": 30, "min_y": 4, "max_y": 7}
    else:
        player_spawn_area = {"min_x": 0, "max_x": 5, "min_y": 0, "max_y": 5}
        enemy_spawn_area = {"min_x": 24, "max_x": 29, "min_y": 17, "max_y": 21}

    # Initialisation du jeu
    enemy_choice = [Salameche('enemy', 0, 0), Carapuce('enemy', 0, 0), Pikachu('enemy', 0, 0), Evoli('enemy', 0, 0), Bulbizarre('enemy', 0, 0), Mewtwo('enemy', 0, 0), Caninos('enemy', 0, 0)]
    enemy_team = random.sample([enemy for enemy in enemy_choice], 3)
    difficulty = difficulty_selector.get_value()[0][1]
    game = Game(screen, player_team, enemy_team, choix_map, difficulty=difficulty)

    # Génération de positions aléatoires pour les Pokémon du joueur
    for pokemon in game.player_units:
        pokemon.x, pokemon.y = generate_random_position(
            game,
            min_x=player_spawn_area["min_x"],
            max_x=player_spawn_area["max_x"],
            min_y=player_spawn_area["min_y"],
            max_y=player_spawn_area["max_y"]
        )

    # Génération de positions aléatoires pour les Pokémon ennemis
    for pokemon in game.enemy_units:
        pokemon.x, pokemon.y = generate_random_position(
            game,
            min_x=enemy_spawn_area["min_x"],
            max_x=enemy_spawn_area["max_x"],
            min_y=enemy_spawn_area["min_y"],
            max_y=enemy_spawn_area["max_y"]
        )

    # Boucle principale du jeu
    while True:
        if game.current_turn == 'player':
            try:
                game.handle_player_turn()  # Gérer le tour du joueur
            except StopIteration:
                pass
        elif game.current_turn == 'enemy':
            game.handle_enemy_turn()  # Gérer le tour de l'ennemi
            if not game.player_units:
                break
            game.current_turn = 'player'  # Passer ensuite le tour au joueur

        game.flip_display()
        pygame.display.flip()

if __name__ == "__main__":
    main()
