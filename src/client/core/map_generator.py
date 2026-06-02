import pygame

background_image = pygame.image.load("map/background.png").convert()
background_w = background_image.get_width()
background_h = background_image.get_height()


def generate_background_surface(width: int, height: int):
    surface = pygame.Surface((width, height))

    columns = int(width / background_w)
    rows = int(height / background_h)

    for y in range(rows):
        for x in range(columns):
            pos_x = x * background_w
            pos_y = y * background_h
            surface.blit(background_image, (pos_x, pos_y))

    return surface
