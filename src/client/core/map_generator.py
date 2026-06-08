import pygame
from .biome import get_bg_data


def generate_background_surface(width: int, height: int):
    img, w, h = get_bg_data()
    surface = pygame.Surface((width, height))

    columns = int(width / w)
    rows = int(height / h)

    for y in range(rows):
        for x in range(columns):
            pos_x = x * w
            pos_y = y * h
            surface.blit(img, (pos_x, pos_y))

    return surface
