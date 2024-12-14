import pygame
from constante import *


class Menu :
    def __init__(self, game):
        self.game = game
        self.current_menu = "main"

    def get_menu_buttons(self):
        """Renvoie la liste des boutons pour le menu actuel."""
        buttons = []

        if self.current_menu == "main":
            # Menu principal avec les actions de base
            buttons = [
                ("Attaquer", self.game.attack_button_rect, lambda: self.switch_to_menu("skills")),
                ("Deplacer", self.game.move_button_rect, lambda: self.game.start_move_action()),
                ("Pokemon", self.game.pokemon_button_rect, lambda: self.switch_to_menu("pokemon")),
                ("Passer le tour", self.game.pass_turn_button_rect, lambda: self.game.end_turn_and_exit())
            ]

        elif self.current_menu == "skills" and self.game.selected_unit:
            # Menu des compétences du Pokémon sélectionné
            buttons = [
                (skill.nom, rect, lambda skill=skill: self.game.use_skill(skill))
                for skill, rect in zip(self.game.selected_unit.capacites, [self.game.attack_button_rect, self.game.move_button_rect, self.game.pokemon_button_rect, self.game.pass_turn_button_rect])
            ]

        elif self.current_menu == "move":
            # Menu de déplacement avec validation ou annulation
            buttons = [
                ("Valider", self.game.attack_button_rect, lambda: self.game.confirm_move()),
                ("Annuler", self.game.move_button_rect, lambda: self.game.cancel_move())
                
            ]

        elif self.current_menu == "pokemon":
            # Menu de sélection de Pokémon dans l'équipe
            buttons = [
                (pokemon.nom, self.get_pokemon_button_rect(i), lambda pokemon=pokemon: self.change_selected_pokemon(pokemon))
                for i, pokemon in enumerate(self.game.player_units)
            ]

        elif self.current_menu == "target":
            # Menu de sélection de cible après avoir choisi une attaque
            targets = self.game.get_available_targets()
            buttons = [
                (f"{target.nom}", self.get_pokemon_button_rect(i), lambda target=target: self.game.attack_target(target))
                for i, target in enumerate(targets)
            ]
            buttons.append(("Retour", self.calculate_back_button_position(len(buttons)), lambda: self.switch_to_menu("skills")))

        # Ajouter le bouton "Retour" de manière dynamique pour tous les menus sauf "main"
        if self.current_menu != "main" and self.current_menu != "target":
            self.game.back_button_rect = self.calculate_back_button_position(len(buttons))
            buttons.append(("Retour", self.game.back_button_rect, lambda: self.switch_to_menu("main")))

        return buttons
    
    def handle_click_on_menu(self, buttons, mouse_x, mouse_y):
        """Gère les clics sur un menu fourni."""
        for button_name, button_rect, action_callback in buttons:
            if button_rect.collidepoint(mouse_x, mouse_y):
                #print(f"Bouton cliqué : {button_name}") #Debug
                action_callback()
                return  # Exécuter l'action du bouton
    
    def draw_menu_2x2(self, menu_title, buttons):
        """Dessine un menu en 2x2 avec les boutons fournis."""
        font_path = "pokemon_generation_1.ttf"
        font = pygame.font.Font(font_path, 14)
        # Afficher le titre du menu
        title_text = font.render(menu_title, True, BLACK)
        title_rect = title_text.get_rect(center=(MAP_WIDTH + ATH_WIDTH // 2, 50))
        self.game.screen.blit(title_text, title_rect)

        # Dessiner les boutons d'action en 2x2
        for i, (button_name, button_rect, _) in enumerate(buttons):
            # Si le bouton correspond à une compétence et que l'indice est valide
            if self.current_menu == "skills" and self.game.selected_unit and i < len(self.game.selected_unit.capacites):
                skill = self.game.selected_unit.capacites[i]
                if self.game.player_action_points < skill.cout_pa:
                    button_color = (100, 100, 100)  # Gris pour les compétences indisponibles
                    text_color = (150, 150, 150)  # Gris clair pour indiquer indisponibilité
                else:
                    button_color = (100, 100, 100)  # Couleur normale
                    text_color = BLACK
            else:
                # Si ce n'est pas un bouton de compétence, utiliser les couleurs normales
                button_color = (100, 100, 100)
                text_color = BLACK

                # Spécial pour "Passer le tour"
                if button_name == "Passer le tour" and self.game.player_action_points == 0:
                    button_color = (255, 255, 0)  # Jaune
                    text_color = (0, 0, 0)  # Noir

            # Dessiner le bouton
            #pygame.draw.rect(self.game.screen, button_color, button_rect)
            # Dessiner le texte avec la couleur appropriée
            button_text = font.render(button_name, True, text_color)
            text_rect = button_text.get_rect(center=button_rect.center)
            self.game.screen.blit(button_text, text_rect)

    def draw_pokemon_selection_menu(self, buttons):
        """Dessine le menu de sélection de Pokémon."""
        font = pygame.font.Font(None, 36)

        # Titre du menu
        title_text = font.render("Choisissez un Pokémon", True, BLACK)
        title_rect = title_text.get_rect(center=(MAP_WIDTH + ATH_WIDTH // 2, 50))
        self.game.screen.blit(title_text, title_rect)

        # Dessiner tous les boutons
        for button_name, button_rect, _ in buttons:
            pygame.draw.rect(self.game.screen, (200, 200, 200), button_rect)
            text_surface = font.render(button_name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=button_rect.center)
            self.game.screen.blit(text_surface, text_rect)

    def switch_to_menu(self, menu_name):
        """Change le menu actuellement affiché."""
        self.current_menu = menu_name
        if menu_name == "skills" and not self.game.selected_unit:
            if self.game.player_units:
                self.game.selected_unit = self.game.player_units[0]
        # Réinitialiser la case surlignée si l'on revient au menu principal
        if menu_name == "main":
            self.game.highlighted_target = None  # Supprimer la surbrillance verte
            self.game.accessible_positions = []  # Réinitialiser les positions accessibles
            self.game.interface.set_info_message("") # Réinitialiser le message d'information ATH
        self.game.flip_display()
        pygame.display.flip()

    def get_pokemon_button_rect(self, index):
        """Renvoie le rectangle pour les boutons de sélection de Pokémon."""
        row = index // 2
        col = index % 2
        x = MAP_WIDTH + ATH_WIDTH // 2 - button_width - padding // 2 + col * (button_width + padding)
        y = 100 + row * (button_height + padding)
        return pygame.Rect(x, y, button_width, button_height)

    def calculate_back_button_position(self, num_buttons):
        """Calcule la position du bouton 'Retour' en fonction du nombre de boutons existants."""
        y_position = 150 + (num_buttons // 2) * (button_height + padding)
        return pygame.Rect(MAP_WIDTH + ATH_WIDTH // 2 - 100, y_position, 200, 50)

    def change_selected_pokemon(self, pokemon):
        """Change le Pokémon actuellement sélectionné."""
        self.game.selected_unit = pokemon
        self.current_menu = "main"  # Revenir au menu principal après la sélection

    def select_pokemon_action(self):
        """Affiche un menu pour choisir un Pokémon de l'équipe du joueur."""
        if not self.game.player_units:
            return
        
        self.current_menu = "pokemon"

        # Boucle de sélection des Pokémon
        selected = False
        while not selected:
            self.game.flip_display()
            pygame.display.flip()

            buttons = [
                (pokemon.nom, self.get_pokemon_button_rect(i), lambda pokemon=pokemon: self.change_selected_pokemon(pokemon))
                for i, pokemon in enumerate(self.game.player_units)
            ]
            buttons.append(("Retour", self.game.back_button_rect, lambda: self.switch_to_menu("main")))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_x, mouse_y = event.pos
                    self.handle_click_on_menu(buttons, mouse_x, mouse_y)

            self.draw_pokemon_selection_menu(buttons)

            if self.current_menu == "main":
                selected = True


