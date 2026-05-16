import random

import noise
import pygame

WATER_COLOR = (65, 105, 225)  # Bleu
FOREST_COLOR = (34, 139, 34)  # Vert
CITY_COLOR = (128, 128, 128)  # Gris

TILE_SIZE = 10


def generate_background_surface(width: int, height: int):

    surface = pygame.Surface((width, height))
    seed = random.randint(0, 1000)
    scale = 20.0

    columns = int(width / TILE_SIZE)
    rows = int(height / TILE_SIZE)

    for y in range(rows):
        for x in range(columns):
            noise_value = noise.pnoise2(
                x / scale,
                y / scale,
                base=seed
            )

            if noise_value < -0.5:
                color = WATER_COLOR
            elif noise_value < 0.2:
                color = FOREST_COLOR
            else:
                color = CITY_COLOR

            rect = (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(surface, color, rect)

    return surface
