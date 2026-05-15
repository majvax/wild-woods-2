from dataclasses import dataclass

import pygame


@dataclass
class Sprite:
    surface: pygame.Surface


@dataclass
class Lifetime:
    time: float
