from typing import cast, final, override

import esper
import pygame

from client.component import Position
from client.core import Engine
from client.factory import create_bandit, create_player
from client.processor import (
    BrainProc,
    InputProc,
    LootProc,
    MovementProc,
    PickupProc,
    RenderProc,
    TargetingProc,
)
from client.processor.damage import DamageProc
from client.processor.death import DeathProc
from .pause import PauseScene
from .scene import Scene


@final
class GameScene(Scene):
    _screen: pygame.Surface
    _timer: float

    def __init__(self, engine: Engine):
        super().__init__()
        self._screen = engine.screen
        self._timer = 0.0
        self._engine = engine

    @override
    def on_enter(self) -> None:
        esper.add_processor(InputProc())
        esper.add_processor(TargetingProc())
        esper.add_processor(BrainProc())
        esper.add_processor(LootProc())
        esper.add_processor(MovementProc())
        esper.add_processor(DamageProc())
        esper.add_processor(PickupProc())
        esper.add_processor(DeathProc(self._engine))
        esper.add_processor(RenderProc(self._screen))

        create_player(Position(self._screen.size[0] / 2, self._screen.size[1] / 2))
        create_bandit(Position(400, 400))

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if cast(int, event.key) in (pygame.K_ESCAPE, pygame.K_p):
                    self._engine.sm.push(PauseScene, self._engine)
                    return True

            if (
                event.type == pygame.USEREVENT
                and event.dict.get("action") == "game_over"
            ):
                from client.scene.GameOver import GameOverScene

                self._engine.sm.push(GameOverScene, self._engine, self.__class__)
                return False

        # Spawn bandits every 5 seconds
        # self._timer += dt
        # if self._timer > 0.1:
        #     pos = Position(
        #         self._screen.get_width() * 0.1
        #         + self._screen.get_width() * 0.8 * random.random(),
        #         self._screen.get_height() * 0.1
        #         + self._screen.get_height() * 0.8 * random.random(),
        #     )
        #     create_bandit(pos)
        #     self._timer = 0

        esper.process(dt)

        return True
