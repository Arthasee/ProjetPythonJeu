# ProjetPythonJeu
Implémenter un simple jeu vidéo de tactique tour par tour en 2D en Python

**Forte inspiration des jeux Fire Emblem**
# Cartes
- Pour la carte on peut essayer de créer 2-3 cartes avec des spécificités particulières (ex: une grotte sombre donne un avantage aux personnages discrets) et des blocs particulier (case eau -> seul les cavaliers peuvent passer)

# Personnages/Classes
- Une classe par personnage afin d'y enregistrer les stats + les compétences
- Faire un système d'équilibrage du style pierre feuille ciseaux (épée bat arc, arc bat lance, lance bat épée par exemple)

# Interface/Gameplay
- Tour par Tour
- Créer un menu de démarrage pour définir le type de jeu, la carte et les personnages choisi
- Interface lors du jeu afin de pouvoir choisir entre se déplacer, attaquer, utiliser une compétence, se défendre

#  des idées pour L'IA 
 
* Niveau  Facile : 
Erreurs volontaires : L'IA peut commettre des erreurs, comme rater des actions ou effectuer des mouvements inutiles.
Vitesse réduite : L'IA agit plus lentement ou avec un délai.
Stratégie simple : L'IA suit des actions prévisibles, par exemple toujours se diriger vers l'objectif le plus proche. 

* Niveau Moyen
Réduction des erreurs : L'IA devient plus précise et fait moins d'erreurs.
Vitesse normale : Les actions de l'IA sont exécutées à un rythme modéré.
Stratégie intermédiaire : L'IA commence à analyser les mouvements du joueur, évite les pièges simples, ou choisit entre plusieurs objectifs.

* Niveau Difficile
Précision élevée : L'IA réagit très rapidement et fait peu d'erreurs.
Anticipation : L'IA prédit les actions du joueur et prend des décisions pour le contrer.
Stratégie avancée : L'IA exploite toutes les mécaniques du jeu de manière optimale (par exemple, utilisation intelligente des zones spécifiques de la carte).
