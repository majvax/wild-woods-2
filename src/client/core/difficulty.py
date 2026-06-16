from dataclasses import dataclass


@dataclass(frozen=True)
class Difficulty:
    name: str
    sheet_path: str
    frame_size: int


# Difficulty isn't wired to gameplay yet — only the selector and the chosen value
# are carried around for now.
DIFFICULTIES: list[Difficulty] = [
    Difficulty("Facile", "assets/map/planet.png", 80),
    Difficulty("Normal", "assets/map/planet.png", 80),
    Difficulty("Difficile", "assets/map/planet.png", 80),
    Difficulty("Impossible", "assets/map/blackhole.png", 200),
]
DEFAULT_DIFFICULTY = 1  # Normal
