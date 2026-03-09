DEHEZ Guillaume
VIARD-CRETAT Hugo
BALLANDRAS Enzo

# Description
Le but du jeu est de faire avancer un convoi militaire dans un monde apocalyptique.
Les joueurs doivent gérer les ressources (essence, nourriture, munitions) et faire face à des événement (attaques de zombies, de bandits, tempêtes de sable, etc...)
Les joueurs auront le choix entre plusieurs chemin pour avancer, chacun avec ses avantages et inconvénients (plus rapide mais plus dangereux, plus long mais plus sûr, etc...)
Le jeu se déroule en temps réel.

Les joueurs peuvent améliorer leur convoi en achetant des remorques sur lesquels il peuvent ajouter des équipements (canons, mitrailleuses, etc...) pour se défendre contre les attaques de zoobies et de bandits.

Tout les x événements, les joueurs rejoignent un camp de survivants où ils peuvent acheter des ressources, équipements, perks, etc...


Les joueurs doivent construire des centres de recherche pour débloquer de nouvelles technologies, améliorer leur convoi et synthétiser l'antidote pour guérir l'humanité du virus qui a transformé les gens en zombies.

Le jeu est fini lorsque les joueurs ont synthétisé l'antidote et sauvé l'humanité, ou lorsque le convoi est détruit ou que les joueurs meurent. 

Une option pour continuer une partie infini est alors proposé, le but étant de survivre le plus longtemps possible et de parcourir la plus grande distance possible.

# Comment jouer ?
Clone le projet:
```bash
git clone https://github.com/majvax/wild-woods-2.git
```
## python
Créer un environnement virtuel
```bash
python3 -m venv .venv
```
Activer l'environnement virtuel
```bash
source .venv/bin/activate # .venv/bin/activate.ps1 pour windows
```
Installer les dépendances
```bash
pip install .
```
Lancer le jeu
```bash
game
```

## uv
Création de l'environnement virtuel et installation des dépendances
```bash
uv sync --no-dev --no-editable
```
Lancer le jeu
```bash
uv run game
```



# Troubleshooting

## fenêtre pygame pas de la bonne taille sur wayland 
sur wayland cette variable d'environnement doit être définie pour que le jeu puisse être affiché correctement:
```bash
SDL_VIDEODRIVER='x11'
```





## Design process

On a décidé de suivre un processus de design simple:
une classe `SceneManageur` qui possède une liste traitée comme une stack de Scene, permettant de mettre à jour et donc d'afficher les différentes scène dans un ordre précis, de la dernière vers la première Scène.

Les Scènes dérives d'une classe abstraite appelée `Scene`.
Les différentes scènes override différentes méthode de la class base.

Chaque Scène possède son propre ecs
