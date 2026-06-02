from typing import final, override

import pygame

from client.core import Engine
from client.ui import NEON_PURPLE, Button

from .scene import Scene


@final
class GameOverScene(Scene):
    _screen: pygame.Surface

    def __init__(self, engine: Engine, game_scene_t: type[Scene]):
        super().__init__()
        self._screen = engine.screen
        self._engine = engine
        self._game_scene_t = game_scene_t

        self._font_subtitle = pygame.font.SysFont("Arial", 24, italic=True)
        self._font_title = pygame.font.Font("assets/fonts/Eater/Eater-Regular.ttf", 150)

        w, h = self._screen.get_size()
        self._btn_quit = Button(
            "Quitter", NEON_PURPLE, 28, 12, 10, 18, on_click=self._quit
        )
        self._btn_replay = Button(
            "Rejouer", NEON_PURPLE, 28, 12, 10, 18, on_click=self._replay
        )

        self._btn_quit.set_rect(w // 2, h // 2 + 100)
        self._btn_replay.set_rect(w // 2, h // 2 + 20)

    def _quit(self) -> None:
        self._engine.stop()

    def _replay(self) -> None:
        self._engine.sm.clear()
        self._engine.sm.push(self._game_scene_t, self._engine)

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        self._screen.fill((15, 0, 0))
        w, h = self._screen.get_size()

        shadow_texte = self._font_title.render("GAME OVER", True, (80, 0, 0))
        rect_shadow = shadow_texte.get_rect(center=(w // 2 + 4, h // 2 - 146))
        self._screen.blit(shadow_texte, rect_shadow)

        image_texte = self._font_title.render("GAME OVER", True, (255, 40, 40))
        rect_texte = image_texte.get_rect(center=(w // 2, h // 2 - 150))
        self._screen.blit(image_texte, rect_texte)

        subtitle = self._font_subtitle.render(
            "L'apocalypse a eu raison de vous...", True, (150, 150, 150)
        )
        rect_sub = subtitle.get_rect(center=(w // 2, h // 2 - 40))
        self._screen.blit(subtitle, rect_sub)

        for btn in (self._btn_replay, self._btn_quit):
            btn.update(dt, events)
            btn.draw(self._screen)

        return False
