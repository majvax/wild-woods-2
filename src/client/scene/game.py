import math
import random
from collections.abc import Callable
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
from client.scene.shop import ShopScene
from client.scene.win import WinScene
from client.view.player import PlayerView

from .pause import PauseScene
from .scene import Scene

_SHOP_RANGE = 200.0


@final
class GameScene(Scene):
    _screen: pygame.Surface
    _timer: float

    def __init__(
        self,
        engine: Engine,
        difficulty: Difficulty = DIFFICULTIES[DEFAULT_DIFFICULTY],
        on_game_over: Callable[[], None] | None = None,
    ):
        super().__init__()
        self._screen = engine.screen
        self._timer = 0.0
        self._engine = engine
        self._game_over_requested = False
        self._difficulty = difficulty
        self._on_game_over_cb = on_game_over
        self._elapsed_time = 0.0
        self._difficulty_level = 0
        self._difficulty_timer = 0.0
        self._shop_counts: list[int] = [0, 0, 0]
        self._open_shop = False
        self._hint_font = pygame.font.SysFont("Arial", 20, bold=True)

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

        create_player(Position(0, 0), health=self._difficulty.player_health)
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

    def _is_near_campfire(self) -> bool:
        campfires = esper.get_components(CampfireTag, Position, Health)
        if not campfires:
            return False
        _, (_, pos, chp) = campfires[0]
        if chp.current <= 0:
            return False
        player_pos = self._get_player_position()
        return math.hypot(player_pos.x - pos.x, player_pos.y - pos.y) < _SHOP_RANGE

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
            create_bandit(
                pos,
                difficulty=self._difficulty_level + self._difficulty.enemy_level_offset,
            )
            return

    def _on_game_over(self) -> None:
        self._game_over_requested = True

    def _on_win(self) -> None:
        on_menu = self._on_game_over_cb or self._engine.stop
        self._engine.sm.clear()
        self._engine.sm.push(WinScene, self._engine, on_menu)

    @override
    def on_exit(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        near_campfire = self._is_near_campfire()

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
            if key == pygame.K_e and near_campfire:
                self._open_shop = True

        self._difficulty_timer += dt
        if self._difficulty_timer >= 10.0:
            self._difficulty_level += 1
            self._difficulty_timer = 0.0

        self._elapsed_time += dt
        spawn_interval = max(
            self._difficulty.spawn_interval_min,
            self._difficulty.spawn_interval_base - self._elapsed_time * 0.02,
        )

        self._timer += dt
        if self._timer > spawn_interval:
            self._spawn_bandit_near_player()
            self._timer = 0

        esper.process(dt)

        # Proximity hint drawn on top of the game render
        if near_campfire:
            w, h = self._screen.get_size()
            hint = self._hint_font.render("E — Boutique", True, pygame.Color("white"))
            shadow = self._hint_font.render("E — Boutique", True, pygame.Color(0, 0, 0))
            cx, cy = w // 2, h - 50
            self._screen.blit(shadow, shadow.get_rect(center=(cx + 1, cy + 1)))
            self._screen.blit(hint, hint.get_rect(center=(cx, cy)))

        # Push shop AFTER rendering so screen.copy() captures the current game frame
        if self._open_shop:
            self._open_shop = False
            player = PlayerView.get()
            weapon = player.weapon()
            if weapon is not None:
                self._engine.sm.push(
                    ShopScene,
                    self._engine,
                    player.hp,
                    weapon,
                    player.inv,
                    self._on_win,
                    self._shop_counts,
                )
                return True

        if self._game_over_requested:
            self._game_over_requested = False
            if self._on_game_over_cb is not None:
                self._engine.sm.push(GameOverScene, self._engine, self._on_game_over_cb)
            return False

        return True
