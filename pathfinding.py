import heapq
from constante import *

class Chemin :
    def __init__(self, game):
        self.game = game

    def calculate_path(self, start_x, start_y, end_x, end_y):
        """Calcule le chemin de la position de départ à la position finale en utilisant l'algorithme A*."""
        open_set = []
        heapq.heappush(open_set, (0, (start_x, start_y)))
        came_from = {}
        g_score = { (start_x, start_y): 0 }
        f_score = { (start_x, start_y): self.heuristic(start_x, start_y, end_x, end_y) }

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == (end_x, end_y):
                return self.reconstruct_path(came_from, current)

            neighbors = self.get_neighbors(current[0], current[1])
            for neighbor in neighbors:
                tentative_g_score = g_score[current] + 1

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self.heuristic(neighbor[0], neighbor[1], end_x, end_y)
                    if neighbor not in [item[1] for item in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))

        return []

    def heuristic(self, x1, y1, x2, y2):
        """Heuristique pour A* (distance de Manhattan)."""
        return abs(x1 - x2) + abs(y1 - y2)

    def get_neighbors(self, x, y):
        """Renvoie les voisins valides (sans collision ni unité) d'une position donnée."""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor_x, neighbor_y = x + dx, y + dy

            if 0 <= neighbor_x < MAP_WIDTH // CELL_SIZE and 0 <= neighbor_y < TOTAL_HEIGHT // CELL_SIZE:
                if not self.game.check_collision(neighbor_x, neighbor_y) and not self.game.is_occupied(neighbor_x, neighbor_y):
                    neighbors.append((neighbor_x, neighbor_y))

        return neighbors

    def reconstruct_path(self, came_from, current):
        """Reconstruit le chemin à partir du dictionnaire came_from."""
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path
