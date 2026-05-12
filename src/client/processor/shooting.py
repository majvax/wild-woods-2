import esper
import pygame
from typing import final, override

@final
class ShootingProc(esper.processor):
    @override
    def on_shoot():
        if event.type == pygame.MOUSEBUTTONUP:
            