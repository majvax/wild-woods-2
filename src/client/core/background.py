import pygame

_bg_image = None
_bg_w: int = 0
_bg_h: int = 0

TILE_SIZE = 10
CHUNK_SIZE_TILES = 32


def get_bg_data() -> tuple[pygame.Surface, int, int]:
    global _bg_image, _bg_w, _bg_h
    if _bg_image is None:
        _bg_image = pygame.image.load("assets/map/background.png").convert()
        _bg_w = _bg_image.get_width()
        _bg_h = _bg_image.get_height()

    return _bg_image, _bg_w, _bg_h
