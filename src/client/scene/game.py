import math
import random
from typing import cast, final, override

import esper
import pygame

from client.component import CampfireTag, Health, Position
from client.core import (
    DEFAULT_DIFFICULTY,
    DIFFICULTIES,
    Difficulty,
    Engine,
)
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
from client.scene.gameover import GameOverScene
from client.view.player import PlayerView

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
        # Menu-selected difficulty: threaded to game-over/replay, no gameplay effect yet.
        self._difficulty = difficulty
        # Time-based difficulty escalation that scales enemy spawn rate and stats.
        self._elapsed_time = 0.0
        self._difficulty_level = 0
        self._difficulty_timer = 0.0

    @override
    def on_enter(self) -> None:
        pygame.mixer.music.load("assets/sound/main-music.mp3")
        pygame.mixer.music.play(-1)
        esper.add_processor(InputProc())
        esper.add_processor(TargetingProc())
        esper.add_processor(BrainProc())
        esper.add_processor(LootProc())
        esper.add_processor(MovementProc())
        esper.add_processor(SpatialGridProc())
        esper.add_processor(DamageProc())
        esper.add_processor(CollisionProc())
        esper.add_processor(DirectionalAnimationProc())
        esper.add_processor(AnimationProc())
        esper.add_processor(CampfireProc())
        esper.add_processor(PickupProc())
        esper.add_processor(DeathProc(self._on_game_over))
        esper.add_processor(ShootingProc())
        esper.add_processor(LifetimeProc())

        esper.add_processor(RenderProc(self._screen, self._engine))

        create_player(Position(0, 0))
        create_campfire(Position(0, 0 - 140))
        self._spawn_bandit_near_player()


    def _get_player_position(self) -> Position:
        player = PlayerView.get()
        return player.pos

    def _get_campfire_position(self) -> Position | None:
        campfires = esper.get_components(CampfireTag, Position)
        if campfires:
            _, (_, pos) = campfires[0]
            return pos
        return None

    def _spawn_bandit_near_player(self) -> None:
        player_pos = self._get_player_position()
        campfire_pos = self._get_campfire_position()
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(300, 800)
            pos = Position(
                player_pos.x + dist * math.cos(angle),
                player_pos.y + dist * math.sin(angle),
            )
            if campfire_pos is not None:
                dx = pos.x - campfire_pos.x
                dy = pos.y - campfire_pos.y
                if math.hypot(dx, dy) < 700:
                    continue
            create_bandit(pos)
            return

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

        self._difficulty_timer += dt  # augmentation de la difficulté
        if self._difficulty_timer >= 10.0:
            self._difficulty_level += 1
            self._difficulty_timer = 0.0

        self._elapsed_time += dt
        spawn_interval = max(0.5, 4.0 - self._elapsed_time * 0.02)

        # Spawn bandits near player every 4 seconds
        self._timer += dt
        if self._timer > spawn_interval:
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
