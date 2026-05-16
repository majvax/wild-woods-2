import random
from typing import cast, final, override

import esper
import pygame

from client.component import PlayerTag, Position
from client.core import CHUNK_SIZE_TILES, TILE_SIZE, Engine
from client.factory import create_bandit, create_player
from client.processor import (
    AnimationProc,
    BrainProc,
    DirectionalAnimationProc,
    InputProc,
    LifetimeProc,
    LootProc,
    MovementProc,
    PickupProc,
    RenderProc,
    ShootingProc,
    SpatialGridProc,
    TargetingProc,
)
from client.processor.damage import DamageProc
from client.processor.death import DeathProc
from client.scene.gameover import GameOverScene

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
        self._game_over_requested = False

    @override
    def on_enter(self) -> None:
        esper.add_processor(InputProc())
        esper.add_processor(TargetingProc())
        esper.add_processor(BrainProc())
        esper.add_processor(LootProc())
        esper.add_processor(MovementProc())
        esper.add_processor(DirectionalAnimationProc())
        esper.add_processor(AnimationProc())
        esper.add_processor(SpatialGridProc())
        esper.add_processor(DamageProc())
        esper.add_processor(PickupProc())
        esper.add_processor(DeathProc(self._on_game_over))
        esper.add_processor(ShootingProc())
        esper.add_processor(LifetimeProc())

        esper.add_processor(RenderProc(self._screen, self._engine))

        chunk_world_size = CHUNK_SIZE_TILES * TILE_SIZE
        create_player(Position(chunk_world_size / 2, chunk_world_size / 2))
        self._spawn_bandit_near_player()

    def _get_player_position(self) -> Position:
        players = esper.get_components(PlayerTag, Position)
        if players:
            _, (_, pos) = players[0]
            return pos
        return Position(0, 0)

    def _spawn_bandit_near_player(self) -> None:
        player_pos = self._get_player_position()
        spawn_radius_x = self._screen.get_width() * 0.8
        spawn_radius_y = self._screen.get_height() * 0.8
        offset_x = (random.random() - 0.5) * spawn_radius_x
        offset_y = (random.random() - 0.5) * spawn_radius_y
        pos = Position(player_pos.x + offset_x, player_pos.y + offset_y)
        create_bandit(pos)

    def _on_game_over(self) -> None:
        self._game_over_requested = True

    @override
    def on_exit(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if cast(int, event.key) in (pygame.K_ESCAPE, pygame.K_p):
                    self._engine.sm.push(PauseScene, self._engine)
                    return True

        # Spawn bandits every 5 seconds
        self._timer += dt

        if self._timer > 4:
            self._spawn_bandit_near_player()
            self._timer = 0

        esper.process(dt)

        if self._game_over_requested:
            self._game_over_requested = False
            self._engine.sm.push(GameOverScene, self._engine, self.__class__)
            return False

        return True
