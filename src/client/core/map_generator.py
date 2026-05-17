import random

import pygame

from .biome import get_tile_color

TILE_SIZE = 10
CHUNK_SIZE_TILES = 32


def generate_background_surface(width: int, height: int):
    surface = pygame.Surface((width, height))
    seed = random.randint(0, 1000)
    scale = 60.0

    columns = int(width / TILE_SIZE)
    rows = int(height / TILE_SIZE)

    for y in range(rows):
        for x in range(columns):
            color = get_tile_color(x, y, seed, scale)

            rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)

    return surface
