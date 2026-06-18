from dataclasses import dataclass


@dataclass(frozen=True)
class Difficulty:
    name: str
    sheet_path: str
    frame_size: int
    player_health: int # joueur : PV de départ
    enemy_level_offset: int # bonus de niveau initial des ennemis (vitesse + PV)
    spawn_interval_base: float # intervalle de base entre les spawns (secondes)
    spawn_interval_min: float # intervalle minimal 

#Difficulty(nom, img, img size, pv, lvl bonus enemy, spawn rate de base, spawn rate max)
DIFFICULTIES: list[Difficulty] = [
    Difficulty("Facile", "assets/map/planet.png", 80, 10, 0, 6.0, 1.0),
    Difficulty("Normal", "assets/map/planet.png", 80, 8, 10, 4.0, 0.8),
    Difficulty("Difficile", "assets/map/planet.png", 80, 6, 20, 3.0, 0.6),
    Difficulty("Impossible", "assets/map/blackhole.png", 200, 4, 30, 2.0, 0.5),
]
DEFAULT_DIFFICULTY = 1  # Normal
