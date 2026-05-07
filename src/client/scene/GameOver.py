from typing import cast, final, override

import pygame

from client.core import Engine
from client.ui import NEON_PURPLE, Button
from client.scene.game import GameScene

from .scene import Scene

@final
class GameOverScene(Scene):
    _screen: pygame.Surface

    def __init__(self, engine: Engine):
        super().__init__()
        self._screen = engine.screen
        self._engine = engine

        self._font_title = pygame.font.SysFont("Arial", 64, bold = True)
    
        w, h = self._screen.get_size()
        self._btn_quit = Button("Quitter", NEON_PURPLE, 28, 12, 10, 18, on_click = self._quit)
        self._btn_replay = Button("Rejouer", NEON_PURPLE, 28, 12, 10,18, on_click = self._replay)

        self._btn_quit.set_rect(w // 2, h // 2 + 100)
        self._btn_replay.set_rect(w // 2, h // 2 + 20)

    def _quit(self) -> None:
        self._engine.stop()
    
    def _replay(self) -> None:
        self._engine.sm.pop()
        self._engine.sm.pop()
        self._engine.sm.push(GameScene, self._engine)

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        self._screen.fill((0, 0, 0))
        image_texte = self._font._title.render("GAME OVER", True, (255, 0, 0))
        w, h = self._screen.get_size()
        rect_texte = image_texte.get_rect(center = (w // 2, h // 2 - 100))
        self._screen.blit(image_texte, rect_texte)

        for btn in (self._btn_replay, self._btn_quit):
            btn.update(dt, events)
            btn.draw(self._screen)
            
        return False