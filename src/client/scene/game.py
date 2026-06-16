import math
import random
from typing import cast, final, override

import esper
import pygame

from client.component import CampfireTag, Health, Position
from client.core import (
    CHUNK_SIZE_TILES,
    DEFAULT_DIFFICULTY,
    DIFFICULTIES,
    TILE_SIZE,
    Difficulty,
    Engine,
)
from client.factory import create_bandit, create_campfire, create_player
from client.view.player import PlayerView
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
from client.scene.gameover import GameOverScene

from .pause import PauseScene
from .scene import Scene


@final
class GameScene(Scene):
    _screen: pygame.Surface
    _timer: float

    def __init__(
        self,
        engine: Engine,
        difficulty: Difficulty = DIFFICULTIES[DEFAULT_DIFFICULTY],
    ):
        super().__init__()
        self._screen = engine.screen
        self._timer = 0.0
        self._engine = engine
        self._game_over_requested = False
        # Stored for now; difficulty does not affect gameplay yet.
        self._difficulty = difficulty

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

        esper.add_processor(RenderProc(self._screen, self._engine))

        chunk_world_size = CHUNK_SIZE_TILES * TILE_SIZE
        cx, cy = chunk_world_size / 2, chunk_world_size / 2
        create_player(Position(cx, cy))
        create_campfire(Position(cx, cy))
        self._spawn_bandit_near_player()

    def _spawn_bandit_near_player(self) -> None:
        player_pos = PlayerView.get().pos
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
            if event.type != pygame.KEYDOWN:
                continue
            key = cast(int, event.key)
            if key in (pygame.K_ESCAPE, pygame.K_p):
                self._engine.sm.push(PauseScene, self._engine)
                return True
            if key == pygame.K_m:
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
            self._engine.sm.push(
                GameOverScene, self._engine, self.__class__, self._difficulty
            )
            return False

        return True
