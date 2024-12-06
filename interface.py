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

        # Afficher les PV du Pokémon joueur
        if self.game.player_units:  # Vérifie si le joueur a des unités
            player_pokemon = self.game.player_units[0]  # Premier Pokémon
            pv_arrondis = math.ceil(player_pokemon.pv)  # Arrondir les PV à l'entier supérieur UNIQUEMENT ATH
            player_hp_text = font_large.render(f"{player_pokemon.nom} : {pv_arrondis}/{player_pokemon.pokemon.stats[0]} PV", True, WHITE)
            self.screen.blit(player_hp_text, (MAP_WIDTH + 10, 300))

        # Afficher les PV du Pokémon ennemi
        if self.game.enemy_units:
            enemy_pokemon = self.game.enemy_units[0]  # Premier Pokémon ennemi
            pv_arrondis = math.ceil(enemy_pokemon.pv)

            # Ajouter la mention "ennemi" si le Pokémon a le même nom que celui du joueur
            if self.game.player_units and enemy_pokemon.nom == self.game.player_units[0].nom:
                enemy_name = f"{enemy_pokemon.nom} ennemi"
            else:
                enemy_name = enemy_pokemon.nom

            enemy_hp_text = font_large.render(f"{enemy_name} : {pv_arrondis}/{enemy_pokemon.pokemon.stats[0]} PV", True, WHITE)
            self.screen.blit(enemy_hp_text, (MAP_WIDTH + 10, 350))

        # Afficher les points d'action du joueur
        if self.game.player_action_points > 0:
            action_points_text = font_medium.render(f"Il te reste {self.game.player_action_points} points d'action à dépenser !", True, WHITE)
        else:
            action_points_text = font_medium.render("Vous n'avez plus de points d'actions.", True, WHITE)
        self.screen.blit(action_points_text, (MAP_WIDTH + 10, 400))

        # Afficher le message d'information
        if hasattr(self, 'info_message') and self.info_message:
            info_text = font_small.render(self.info_message, True, WHITE)
            self.screen.blit(info_text, (MAP_WIDTH + 10, 450))

        # Indicateur nerfs du Pokémon joueur
        if self.game.player_units:
            player_nerfs_summary = f"{player_pokemon.nom} : "
            for stat, baisse in player_pokemon.nerfs.items():
                if baisse > 0:
                    player_nerfs_summary += f"{baisse} baisse(s) de {stat}, "
            player_nerfs_summary = player_nerfs_summary.rstrip(", ")
            player_nerfs_text = font_small.render(player_nerfs_summary, True, WHITE)
            self.screen.blit(player_nerfs_text, (MAP_WIDTH + 10, 500))

        # Indicateur nerfs du Pokémon adverse
        if self.game.enemy_units:
            enemy_nerfs_summary = f"{enemy_name} : "
            for stat, baisse in enemy_pokemon.nerfs.items():
                if baisse > 0:
                    enemy_nerfs_summary += f"{baisse} baisse(s) de {stat}, "
            enemy_nerfs_summary = enemy_nerfs_summary.rstrip(", ")
            enemy_nerfs_text = font_small.render(enemy_nerfs_summary, True, WHITE)
            self.screen.blit(enemy_nerfs_text, (MAP_WIDTH + 10, 600))

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
                    "pokemon": "Choisissez un Pokémon"
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
