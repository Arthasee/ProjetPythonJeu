import pygame
import math
from constante import *
from menus import Menu

class Interface :
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.menu = Menu(self.game)

    def draw_ath(self):
        """Dessine l'ATH sur le côté droit"""
        ath_rect = pygame.Rect(MAP_WIDTH, 0, ATH_WIDTH, TOTAL_HEIGHT)  # Zone de l'ATH
        pygame.draw.rect(self.screen, (50, 50, 50), ath_rect)  # Fond gris foncé de l'ATH droit
        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 24)

        y_offset = 325  # Position de départ pour afficher les informations sur les Pokémon

        # Afficher les PV de tous les Pokémon du joueur
        for player_pokemon in self.game.player_units:
            pv_arrondis = math.ceil(player_pokemon.pv)# Arrondir les PV à l'entier supérieur UNIQUEMENT ATH
            pv_max = player_pokemon.pokemon.stats[0]  # Utilisation de pokemon.stats[0] pour les PV max
            health_text = f"{player_pokemon.nom} PV: {pv_arrondis}/{pv_max}"
            text_surface = font_small.render(health_text, True, (255, 255, 255))  # Couleur blanche pour les joueurs
            text_rect = text_surface.get_rect(topleft=(MAP_WIDTH + 10, y_offset))
            self.game.screen.blit(text_surface, text_rect)
            y_offset += 30

        # Ajouter un espace entre les Pokémon du joueur et les ennemis
        y_offset += 20

        # Afficher les PV de tous les Pokémon ennemis
        for enemy_pokemon in self.game.enemy_units:
            pv_arrondis = math.ceil(enemy_pokemon.pv)
            pv_max = enemy_pokemon.pokemon.stats[0]  # Utilisation de pokemon.stats[0] pour les PV max

            # Ajouter la mention "ennemi" si le Pokémon a le même nom qu'un Pokémon du joueur
            if any(enemy_pokemon.nom == player_pokemon.nom for player_pokemon in self.game.player_units):
                enemy_name = f"{enemy_pokemon.nom} ennemi"
            else:
                enemy_name = enemy_pokemon.nom

            health_text = f"{enemy_name} PV: {pv_arrondis}/{pv_max}"
            text_surface = font_small.render(health_text, True, (255, 0, 0))  # Rouge pour les ennemis
            text_rect = text_surface.get_rect(topleft=(MAP_WIDTH + 10, y_offset))
            self.game.screen.blit(text_surface, text_rect)
            y_offset += 30

        # Afficher les points d'action du joueur
        if self.game.player_action_points > 0:
            action_points_text = font_medium.render(f"Il te reste {self.game.player_action_points} points d'action à dépenser !", True, WHITE)
        else:
            action_points_text = font_medium.render("Vous n'avez plus de points d'actions.", True, WHITE)
        self.screen.blit(action_points_text, (MAP_WIDTH + 10, 290))

        y_offset += 50

        # Afficher le message d'information
        if hasattr(self, 'info_message') and self.info_message:
            info_text = font_small.render(self.info_message, True, WHITE)
            self.screen.blit(info_text, (MAP_WIDTH + 10, 270))

        # Afficher les nerfs des Pokémon qui ont été affectés

        for nerfed_pokemon in self.game.nerfed_units:
            # Affiche le nom du Pokémon d'abord
            if nerfed_pokemon in self.game.enemy_units and any(nerfed_pokemon.nom == player_pokemon.nom for player_pokemon in self.game.player_units):
                pokemon_name_text = font_small.render(f"{nerfed_pokemon.nom} ennemi :", True, WHITE)
            else:
                pokemon_name_text = font_small.render(f"{nerfed_pokemon.nom} :", True, WHITE)
            self.screen.blit(pokemon_name_text, (MAP_WIDTH + 10, y_offset))
            y_offset += 20  # Décale pour afficher les nerfs en dessous

            # Affiche chaque nerf sur une nouvelle ligne
            for stat, baisse in nerfed_pokemon.nerfs.items():
                if baisse > 0:
                    nerf_text = font_small.render(f"  -{baisse} {stat}", True, (255, 255, 255))
                    self.screen.blit(nerf_text, (MAP_WIDTH + 20, y_offset))
                    y_offset += 20  # Décale pour chaque ligne de nerf

            # Ajoute un espace après les nerfs d'un Pokémon avant le suivant
            y_offset += 10

        # Obtenir les boutons en fonction du menu actuel
        buttons = self.game.menu.get_menu_buttons()

        # Utiliser `draw_menu_2x2` pour dessiner tous les boutons de l'ATH
        if buttons:
            if self.game.menu.current_menu == "main" and self.game.selected_unit:
                menu_title = f"Que va faire {self.game.selected_unit.nom} ?"
            else:
                menu_title = {
                    "skills": "Compétences",
                    "move": "Déplacement",
                    "pokemon": "Choisissez un Pokémon",
                    "target": "Choisissez une cible"
                }.get(self.game.menu.current_menu, "")

        self.game.menu.draw_menu_2x2(menu_title, buttons)

    def highlight_positions(self, positions, color, alpha=178): 
        """Permet la coloration des cases de potentiels déplacements lors du tour"""
        # Créer une surface avec transparence
        highlight_surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
        r, g, b = color
        highlight_surface.fill((r, g, b, alpha))  # Remplir avec la couleur et l'opacité

        for x, y in positions:
            self.screen.blit(highlight_surface, (x * CELL_SIZE, y * CELL_SIZE))

    def add_message(self, message):
        """Ajoute un message d'information à la liste des messages disponibles."""
        if not hasattr(self, 'messages'):
            self.messages = []
        self.messages.append(message)

    def display_message_by_id(self, message_id):
        """Affiche un message d'information basé sur l'ID du message dans la liste des messages."""
        if hasattr(self, 'messages') and 0 <= message_id < len(self.messages):
            self.set_info_message(self.messages[message_id])

    def set_info_message(self, message):
        """Met à jour le message d'information à afficher dans l'ATH."""
        self.info_message = message
        self.draw_ath()  # Mettre à jour l'ATH après la modification du message
        pygame.display.flip()

    def initialize_messages(self):
        """Initialise la liste des messages prédéfinis."""
        self.add_message("")  # Réinitialiser le message
        self.add_message("L'ennemi est trop loin pour être attaqué.")
        self.add_message("Aucun ennemi disponible pour cette attaque.")
        self.add_message("Pas assez de points d'action pour attaquer.")
