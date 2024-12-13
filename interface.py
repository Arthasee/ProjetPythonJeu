import pygame
import math
from constante import *
from menus import Menu

class Interface:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.menu = Menu(self.game)
        self.ath_background = pygame.image.load("background.webp")  # Charge l'image de fond pour l'ATH
    
    def draw_ath(self):
        """Dessine l'ATH sur le côté droit"""
        ath_rect = pygame.Rect(MAP_WIDTH, 0, ATH_WIDTH, TOTAL_HEIGHT)  # Zone de l'ATH

        # Dessiner l'image de fond pour l'ATH
        self.screen.blit(self.ath_background, (MAP_WIDTH, 0))

        font_large = pygame.font.Font(None, 36)
        font_medium = pygame.font.Font(None, 28)
        font_small = pygame.font.Font(None, 24)

        y_offset = 325  # Position de départ pour afficher les informations sur les Pokémon
        center_x = MAP_WIDTH + (ATH_WIDTH // 2)  # Calcul du centre horizontal de l'ATH

        # Afficher les PV de tous les Pokémon du joueur
        for player_pokemon in self.game.player_units:
            pv_arrondis = math.ceil(player_pokemon.pv)  # Arrondir les PV à l'entier supérieur UNIQUEMENT ATH
            pv_max = player_pokemon.pv_max  # Utilisation de pokemon.stats[0] pour les PV max
            health_text = f"{player_pokemon.nom}"
            text_surface = font_small.render(health_text, True, BLACK)  # Couleur noir pour les joueurs
            text_rect = text_surface.get_rect(center=(center_x, y_offset))  # Centrer le texte
            self.game.screen.blit(text_surface, text_rect)
            y_offset += 20

            # Affichage de la barre de PV centrée
            self.draw_health_bar(center_x - 100, y_offset, pv_arrondis, pv_max)  # Déplacer la barre pour la centrer
            y_offset += 40  # Ajuste pour l'espacement

        # Ajouter un espace entre les Pokémon du joueur et les ennemis
        y_offset += 60

        # Afficher les PV de tous les Pokémon ennemis
        for enemy_pokemon in self.game.enemy_units:
            pv_arrondis = math.ceil(enemy_pokemon.pv)
            pv_max = enemy_pokemon.pv_max  # Utilisation de pokemon.stats[0] pour les PV max

            # Ajouter la mention "ennemi" si le Pokémon a le même nom qu'un Pokémon du joueur
            if any(enemy_pokemon.nom == player_pokemon.nom for player_pokemon in self.game.player_units):
                enemy_name = f"{enemy_pokemon.nom} ennemi"
            else:
                enemy_name = enemy_pokemon.nom

            health_text = f"{enemy_name}  "
            text_surface = font_small.render(health_text, True,  (255,255, 255))   
            text_rect = text_surface.get_rect(center=(center_x, y_offset))  # Centrer le texte
            self.game.screen.blit(text_surface, text_rect)
            y_offset += 20

            # Affichage de la barre de PV centrée
            self.draw_health_bar(center_x - 100, y_offset, pv_arrondis, pv_max)  # Déplacer la barre pour la centrer
            y_offset += 40  # Ajuste pour l'espacement

        # Afficher les points d'action du joueur
        if self.game.player_action_points > 0:
            action_points_text = font_medium.render(f"Il te reste {self.game.player_action_points} points d'action à dépenser !", True, BLACK)
        else:
            action_points_text = font_medium.render("Vous n'avez plus de points d'actions.", True, BLACK)
        
        action_points_text_rect = action_points_text.get_rect(center=(center_x, 290))  # Centrer le texte
        self.screen.blit(action_points_text, action_points_text_rect)

        y_offset += 60

        # Afficher le message d'information
        if hasattr(self, 'info_message') and self.info_message:
            info_text = font_small.render(self.info_message, True, BLACK)
            info_text_rect = info_text.get_rect(center=(center_x, 270))  # Centrer le message
            self.screen.blit(info_text, info_text_rect)

        # Afficher les nerfs des Pokémon qui ont été affectés
        for nerfed_pokemon in self.game.nerfed_units:
            # Affiche le nom du Pokémon d'abord
            if nerfed_pokemon in self.game.enemy_units and any(nerfed_pokemon.nom == player_pokemon.nom for player_pokemon in self.game.player_units):
                pokemon_name_text = font_small.render(f"{nerfed_pokemon.nom} ennemi :", True, BLACK)
            else:
                pokemon_name_text = font_small.render(f"{nerfed_pokemon.nom} :", True, BLACK)
            pokemon_name_text_rect = pokemon_name_text.get_rect(center=(center_x, y_offset))  # Centrer le texte
            self.screen.blit(pokemon_name_text, pokemon_name_text_rect)
            y_offset += 20  # Décale pour afficher les nerfs en dessous

            # Affiche chaque nerf sur une nouvelle ligne
            for stat, baisse in nerfed_pokemon.nerfs.items():
                if baisse > 0:
                    nerf_text = font_small.render(f"  -{baisse} {stat}", True, BLACK)
                    nerf_text_rect = nerf_text.get_rect(center=(center_x, y_offset))  # Centrer le texte
                    self.screen.blit(nerf_text, nerf_text_rect)
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

    def draw_health_bar(self, x, y, current_hp, max_hp, width=200, height=15):
        """Dessine une barre de PV."""
        # Dessiner le fond de la barre de PV
        pygame.draw.rect(self.screen, (30, 30, 30), (x, y, width, height))
        
        # Calculer la largeur de la barre de PV en fonction des PV actuels
        health_width = width * (current_hp / max_hp)
        
        # Récupérer la couleur en fonction de la santé
        bar_color = self.get_health_bar_color(current_hp, max_hp)
        
        # Dessiner la barre de PV
        pygame.draw.rect(self.screen, bar_color, (x, y, health_width, height))

    def get_health_bar_color(self, current_hp, max_hp):
        """Retourne la couleur de la barre de PV en fonction de la santé."""
        ratio = current_hp / max_hp
        if ratio > 0.7:
            return (0, 255, 0)  # Vert pour une bonne santé
        elif ratio > 0.3:
            return (255, 255, 0)  # Jaune pour une santé moyenne
        else:
            return (255, 0, 0)  # Rouge pour une faible santé

    def draw_ath_background(self):
        """Dessine un fond dégradé pour l'ATH."""
        for i in range(ATH_WIDTH):
            color = (i // 2, i // 4, i // 6)  # Crée un dégradé de couleur
            pygame.draw.line(self.screen, color, (MAP_WIDTH + i, 0), (MAP_WIDTH + i, TOTAL_HEIGHT))

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
