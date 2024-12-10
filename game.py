"""Fichier du jeu principal
    """
import random
import pygame
import pygame_menu
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

    def __init__(self, screen, player, enemy, carte):
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
        self.chemin = Chemin(self)  # Instanciation de l'objet Chemin
        self.interface = Interface(self) # Instanciation de l'objet Interface
        self.menu = Menu(self)  # Instanciation de l'objet Menu
        
        pygame.mixer.init()
        pygame.mixer.music.load("music/battle.mp3")
        pygame.mixer.music.play()
        
        self.current_turn = 'player' # Commence par le tour du joueur
        self.player_units = player
        self.enemy_units = enemy
        self.selected_unit = self.player_units[0] if self.player_units else None # Unité sélectionnée par défaut
        self.show_skills = False # indicateur pour menu compétences
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
        print("Début du tour du joueur")
        self.player_action_points = 10  # Réinitialise les points d'actions au début du tour
        if not self.selected_unit and self.player_units: # Si pas d'unité sélectionnée et qu'il y a des unités jouables
            self.info_message = "Unité sélectionnée par défaut : {}".format(self.player_units[0].nom)
            self.selected_unit = self.player_units[0] # Sélectionner la première unité jouable par défaut

        try:
            while True:  # Permet de continuer le tour jusqu'à ce que le joueur termine manuellement
                # Rafraîchir l'affichage avec les surlignages
                if self.menu.current_menu == "move":
                    self.flip_display(highlight_positions=self.accessible_positions, highlight_color=(135, 206, 235))
                else:
                    self.flip_display()
                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        exit()

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_x, mouse_y = event.pos
                        buttons = []

                        if self.menu.current_menu == "main":
                            buttons = [
                                ("Attaquer", self.attack_button_rect, lambda: self.start_attack_action()),
                                ("Déplacer", self.move_button_rect, lambda: self.start_move_action()),
                                ("Pokémon", self.pokemon_button_rect, lambda: self.menu.select_pokemon_action()),
                                ("Passer le tour", self.pass_turn_button_rect, lambda: self.end_turn_and_exit())
                            ]

                        elif self.menu.current_menu == "skills" and self.selected_unit:
                            buttons = [
                                (skill.nom, rect, lambda skill=skill: self.use_skill(skill))
                                for skill, rect in zip(self.selected_unit.capacites, [self.attack_button_rect, self.move_button_rect, self.pokemon_button_rect, self.pass_turn_button_rect])
                            ]
                            buttons.append(("Retour", self.back_button_rect, lambda: self.menu.switch_to_menu("main")))

                        elif self.menu.current_menu == "move":
                            buttons = [
                                ("Valider", self.attack_button_rect, lambda: self.confirm_move()),
                                ("Annuler", self.move_button_rect, lambda: self.cancel_move()),
                                ("Retour", self.back_button_rect, lambda: self.menu.switch_to_menu("main"))
                            ]

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
                                    cost_message = f"Ce déplacement coûtera {distance} points d'action."
                                    self.interface.set_info_message(cost_message)
                                    self.flip_display()  # Rafraîchir l'affichage pour inclure la nouvelle case surlignée
                                    pygame.display.flip()

                    # Survol des compétences avec la souris pour afficher le nom de la compétence
                    if event.type == pygame.MOUSEMOTION and self.menu.current_menu == "skills" and self.selected_unit:
                        mouse_x, mouse_y = event.pos
                        for skill, rect in zip(self.selected_unit.capacites, [self.attack_button_rect, self.move_button_rect, self.pokemon_button_rect, self.pass_turn_button_rect]):
                            if rect.collidepoint(mouse_x, mouse_y):
                                cost_message = f"Utiliser {skill.nom} coûtera {skill.cout_pa} points d'action."
                                self.interface.set_info_message(cost_message)
                                break
                        else:
                            self.interface.set_info_message("") # Si la souris n'est sur aucune compétence, on réinitialise le message

                self.interface.draw_ath() # Dessiner l'ATH à chaque itération
                
        except StopIteration:
            print("Tour du joueur terminé, passant au tour de l'ennemi")
            pass # Sortir de la boucle proprement lorsque le tour se termine

    def handle_enemy_turn(self):
        """IA qui effectue des déplacements et des attaques."""
        self.enemy_action_points = 10  # Réinitialise les points d'actions (PA) au début du tour pour l'IA

        for enemy in self.enemy_units:
            if not self.player_units:
                pygame.quit()
                exit()

            # Sélectionner une unité cible parmi les unités du joueur
            target = random.choice(self.player_units)

            # Calculer les positions accessibles pour l'ennemi
            # accessible_positions = self.get_accessible_positions(enemy, max_distance=10)

            while self.enemy_action_points > 0:
                accessible_positions = self.get_accessible_positions(enemy, max_distance=10)
                distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
                # Tenter d'attaquer si à portée
                if distance == 1:
                    available_skills = [s for s in enemy.capacites if s.cout_pa <= self.enemy_action_points]
                    if available_skills:
                        skill = random.choice(available_skills)
                        enemy.attaquer(skill, target, self.screen)
                        self.enemy_action_points -= skill.cout_pa
                        if target.pv <= 0:
                            self.player_units.remove(target)
                        break  # Fin des actions pour cet ennemi
                    else:
                        break  # Pas de compétences disponibles, passer au prochain ennemi

                # Tenter de se déplacer vers la cible si elle n'est pas à portée
                elif distance > 1 and accessible_positions:
                    target_position = min(accessible_positions, key=lambda pos: abs(pos[0] - target.x) + abs(pos[1] - target.y))
                    path = self.chemin.calculate_path(enemy.x, enemy.y, target_position[0], target_position[1])
                    print("on a trouvé ",len(accessible_positions))
                    # Animer le déplacement du Pokémon le long du chemin
                    for (x, y) in path:
                        if self.enemy_action_points <= 0:
                            break
                        if (x, y) in accessible_positions and not self.check_collision(x, y) and not self.is_occupied(x, y):
                            enemy.x = x
                            enemy.y = y
                            self.flip_display()  # Mettre à jour l'affichage après chaque déplacement
                            pygame.display.flip()
                            self.clock.tick(5)  # Contrôler la vitesse de l'animation
                            self.enemy_action_points -= 1

                    # Recalculer la distance après le déplacement
                    distance = abs(enemy.x - target.x) + abs(enemy.y - target.y)
                    if distance == 1:
                        available_skills = [s for s in enemy.capacites if s.cout_pa <= self.enemy_action_points]
                        if available_skills:
                            skill = random.choice(available_skills)
                            enemy.attaquer(skill, target, self.screen)
                            self.enemy_action_points -= skill.cout_pa
                            if target.pv <= 0:
                                self.player_units.remove(target)
                        break  # Fin des actions pour cet ennemi

                # Si aucune action n'est possible, terminer les actions de l'ennemi
                else:
                    break

            # Réinitialiser l'affichage à la fin des actions de l'ennemi
            self.flip_display()
            pygame.display.flip()

        # Passer au tour du joueur après avoir terminé toutes les actions ennemies
        self.current_turn = 'player'
        self.player_action_points = 10
    
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
        print(f"Fin du tour (end_turn): {self.current_turn}")
        self.current_turn = 'enemy' if self.current_turn == 'player' else 'player'
        print(f"Nouveau tour : {self.current_turn}")
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
                path = self.chemin.calculate_path(unit.x, unit.y, x, y)
                if len(path) - 1 <= max_distance:  # Vérifier que le chemin réel respecte les points d'action disponibles
                    positions.add((x, y))

            # Ajouter les positions adjacentes
            if distance < max_distance:
                if x > 0:
                    queue.append((x - 1, y, distance + 1))
                if x < MAP_WIDTH // CELL_SIZE - 1:
                    queue.append((x + 1, y, distance + 1))
                if y > 0:
                    queue.append((x, y - 1, distance + 1))
                if y < TOTAL_HEIGHT // CELL_SIZE - 1:
                    queue.append((x, y + 1, distance + 1))

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
                # print(f"Collision détectée avec {rect}")
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

            # Calculer les positions accessibles pour l'unité sélectionnée
            max_distance = self.player_action_points  # La portée dépend des points d'action disponibles
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
            path = self.chemin.calculate_path(start_x, start_y, end_x, end_y)

            # Animer le déplacement du Pokémon le long du chemin
            for (x, y) in path:
                self.selected_unit.x = x
                self.selected_unit.y = y
                self.flip_display()  # Mettre à jour l'affichage après chaque déplacement
                pygame.display.flip()
                self.clock.tick(5)  # Contrôler la vitesse de l'animation (plus grand = plus lent)

            # Déduire les points d'action en fonction de la distance parcourue
            distance_moved = len(path) - 1
            if self.player_action_points >= distance_moved:
                self.player_action_points -= distance_moved
                self.menu.current_menu = "main"
                self.accessible_positions = []
                self.highlighted_target = None
            else:
                self.cancel_move()
            self.interface.set_info_message("")
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
        # Vérifier si le joueur a assez de PA pour attaquer
        if self.player_action_points >= 6:
            if self.enemy_units:
                target = self.enemy_units[0]  # Cible par défaut
                distance = abs(self.selected_unit.x - target.x) + abs(self.selected_unit.y - target.y)
                if distance > 6:
                    self.interface.display_message_by_id(1)  # L'ennemi est trop loin pour être attaqué
                else:
                    # Vérifier le type de compétence (attaque ou non attaque)
                    if skill.categorie == "attaque":
                        self.selected_unit.attaquer(skill, target, self.screen)  # Attaque
                        self.interface.set_info_message(f"{self.selected_unit.nom} utilise {skill.nom} !")
                    elif skill.categorie == "non-attaque":
                        self.selected_unit.non_attaquer(skill, target)  # Utiliser la compétence de type non attaque sur la cible
                        self.interface.set_info_message(f"{self.selected_unit.nom} utilise {skill.nom} ! {skill.stat} a diminué.")

                    self.player_action_points -= 6  # Déduire les PA nécessaires

                    # Vérifier si le Pokémon adverse est vaincu
                    if target.pv <= 0:
                        self.interface.set_info_message(f"{target.nom} a été vaincu!")
                        self.enemy_units.remove(target)

                        # Vérifier la condition de victoire
                        if not self.enemy_units:
                            pygame.quit()
                            exit()
            else:
                self.interface.display_message_by_id(2)  # Aucun ennemi disponible pour cette attaque
        else:
            self.interface.display_message_by_id(3)  # Pas assez de points d'action pour attaquer

def main():
    """Fonction principal
    """
    # Initialisation de Pygame
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("music/1-03. Title Screen.mp3")
    pygame.mixer.music.play()
    
    # Instanciation de la fenêtre
    screen = pygame.display.set_mode((TOTAL_WIDTH, TOTAL_HEIGHT))
    pygame.display.set_caption("PokeBattle")
    menu = pygame_menu.Menu('Welcome', TOTAL_WIDTH, TOTAL_HEIGHT,
                        theme=pygame_menu.themes.THEME_BLUE, position=(50,50, True))
    # Instanciation du jeu
    player_team = []
    player_team.append(Pokemon(Carapuce(),'player', 0, 0))
    enemy_choice = [Pokemon(Salameche(), 'ennemy', 31, 23),Pokemon(Carapuce(),'ennemy', 31, 23),Pokemon(Pikachu(),'ennemy', 31, 23),Pokemon(Evoli(),'ennemy', 31, 23),Pokemon(Bulbizarre(),'ennemy', 31, 23),
                    Pokemon(Mewtwo(),'ennemy', 31, 23), Pokemon(Caninos(),'ennemy', 31, 23)]
    choix = random.randint(0,4)
    choix_map = ""
    
    selecteur_poke = menu.add.selector('Pokémon :', [('Salamèche', 1), ('Carapuce', 2), ('Pikachu', 3), ('Évoli', 4), ('Bulbizarre', 5), ('Mewtwo', 6), ('Caninos', 7)])
    selecteur_carte = menu.add.selector('Carte :', [('Ville', 1), ('Plage', 2), ('Grotte', 3)])
    menu.add.button('Play', menu.disable)
    menu.add.button('Quit', pygame_menu.events.EXIT)
    menu.add.image("sprite/rfvf/4.png", scale=(1,1))
    menu.add.image("sprite/rfvf/7.png", scale=(1,1))
    menu.add.image("sprite/rfvf/25.png", scale=(1,1))
    menu.add.image("sprite/rfvf/133.png", scale=(1,1))
    menu.mainloop(surface)
    
    if selecteur_poke.get_index() == 0:
        player_team[0] = Pokemon(Salameche(), 'player', 0, 0)
    if selecteur_poke.get_index() == 1:
        player_team[0] = Pokemon(Carapuce(),'player', 0, 0)
    if selecteur_poke.get_index() == 2:
        player_team[0] = Pokemon(Pikachu(),'player', 0, 0)
    if selecteur_poke.get_index() == 3:
        player_team[0] = Pokemon(Evoli(),'player', 0, 0)
    if selecteur_poke.get_index() == 4:
        player_team[0] = Pokemon(Bulbizarre(),'player', 0, 0)
    if selecteur_poke.get_index() == 5:
        player_team[0] = Pokemon(Mewtwo(),'player', 0, 0)
    if selecteur_poke.get_index() == 6:
        player_team[0] = Pokemon(Caninos(),'player', 0, 0)
    if selecteur_carte.get_index() == 0:
        choix_map = "map_1.tmx"
    if selecteur_carte.get_index() == 1:
        choix_map = "map_2.tmx"
    if selecteur_carte.get_index() == 2:
        choix_map = "map_3.tmx"
    pygame.mixer.music.pause()
    game = Game(screen, player_team,[enemy_choice[choix]], choix_map)
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
