from typing import final, override

import pygame

from client.core import Engine
from client.scene.game import GameScene
from client.ui.components import NEON_PURPLE, Button

from .scene import Scene


@final
class MainMenuScene(Scene):
    def __init__(self, engine: Engine):
        super().__init__()
        self._engine = engine
        self._screen = engine.screen
        self._font = pygame.font.SysFont("Arial", 42)
        self._subtitle = pygame.font.SysFont("Arial", 22)
        self._start_requested = False
        self._start_button = Button(
            text="Start",
            colors=NEON_PURPLE,
            padding_x=30,
            padding_y=12,
            radius=8,
            font_size=24,
            on_click=self._start_game,
        )

    def _start_game(self) -> None:
        self._start_requested = True

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        width, height = self._screen.get_size()
        self._screen.fill(pygame.Color(20, 20, 30))

        title = self._font.render("Wild Woods 2", True, pygame.Color("white"))
        subtitle = self._subtitle.render(
            "Press Start to begin", True, pygame.Color(180, 180, 200)
        )

        self._screen.blit(title, title.get_rect(center=(width // 2, height // 2 - 120)))
        self._screen.blit(
            subtitle, subtitle.get_rect(center=(width // 2, height // 2 - 70))
        )

        self._start_button.set_rect(width // 2, height // 2)
        self._start_button.update(dt, events)
        self._start_button.draw(self._screen)

        if self._start_requested:
            self._engine.sm.pop()
            self._engine.sm.push(GameScene, self._engine)
            return False

        return False
