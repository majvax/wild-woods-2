import math
import random
from typing import cast, final, override

import esper
import pygame

from client.component import CampfireTag, Health, PlayerTag, Position
from client.core import CHUNK_SIZE_TILES, TILE_SIZE, Engine
from client.factory import create_bandit, create_campfire, create_player
from client.processor import (
    AnimationProc,
    BrainProc,
    CampfireProc,
    CollisionProc,
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
from client.processor.render_helpers import ChunkRenderer
from client.scene.gameover import GameOverScene

from .pause import PauseScene
from .scene import Scene


@final
class GameScene(Scene):
    _screen: pygame.Surface
    _timer: float

    def __init__(self, engine: Engine, chunk_renderer: ChunkRenderer | None = None):
        super().__init__()
        self._screen = engine.screen
        self._timer = 0.0
        self._engine = engine
        self._game_over_requested = False
        self._chunk_renderer = chunk_renderer

    @override
    def on_enter(self) -> None:
        pygame.mixer.music.load("assets/sound/main-music.mp3")
        pygame.mixer.music.play(-1)
        esper.add_processor(InputProc())
        esper.add_processor(TargetingProc())
        esper.add_processor(BrainProc())
        esper.add_processor(LootProc())
        esper.add_processor(MovementProc())
        esper.add_processor(CollisionProc())
        esper.add_processor(DirectionalAnimationProc())
        esper.add_processor(AnimationProc())
        esper.add_processor(CampfireProc())
        esper.add_processor(SpatialGridProc())
        esper.add_processor(DamageProc())
        esper.add_processor(PickupProc())
        esper.add_processor(DeathProc(self._on_game_over))
        esper.add_processor(ShootingProc())
        esper.add_processor(LifetimeProc())

        if self._chunk_renderer is None:
            esper.add_processor(RenderProc(self._screen, self._engine))
        else:
            esper.add_processor(
                RenderProc(
                    self._screen,
                    self._engine,
                    chunk_renderer=self._chunk_renderer,
                )
            )

        chunk_world_size = CHUNK_SIZE_TILES * TILE_SIZE
        cx, cy = chunk_world_size / 2, chunk_world_size / 2
        create_player(Position(cx, cy))
        create_campfire(Position(cx, cy))
        self._spawn_bandit_near_player()

    def _get_player_position(self) -> Position:
        players = esper.get_components(PlayerTag, Position)
        if players:
            _, (_, pos) = players[0]
            return pos
        return Position(0, 0)

    def _spawn_bandit_near_player(self) -> None:
        player_pos = self._get_player_position()
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(300, 500)
        pos = Position(
            player_pos.x + dist * math.cos(angle), player_pos.y + dist * math.sin(angle)
        )
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
                if cast(int, event.key) == pygame.K_m:
                    for _, (_, health) in esper.get_components(CampfireTag, Health):
                        health.current = max(0.0, health.current - 10.0)

        # Spawn bandits near player every 4 seconds
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
