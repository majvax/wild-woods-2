from dataclasses import dataclass, field
from enum import IntEnum, auto

import esper
import pygame

from client.component import (
    AI,
    AnimationClip,
    AnimationRuntime,
    AnimationSet,
    AnimationState,
    DamageDealer,
    DirectionalAnimation,
    EnemyTag,
    Health,
    Hitbox,
    ItemKind,
    LootTable,
    LootTableKind,
    PatrolRuntime,
    PatrolSettings,
    Position,
    Speed,
    Sprite,
    Targeting,
    Velocity,
)

_DIRECTIONS = ("up", "down", "left", "right")
_RUN_FRAME_COUNT = 9
_RUN_PATH = "assets/sprite/ennemis/run/{direction}/{i}.png"


class EnemyArchetype(IntEnum):
    BANDIT = auto()
    SCOUT = auto()
    BRUTE = auto()


@dataclass(frozen=True)
class EnemyStats:
    speed_base: float
    speed_per_level: float
    health_base: float
    health_per_level: float
    damage: float
    targeting_range: float
    scale: float
    tint: tuple[int, int, int] | None
    loot: list[tuple[ItemKind, float]] = field(default_factory=list)


# Per-archetype tuning. BANDIT mirrors the historical bandit so existing
# behaviour (and tests) stay unchanged; SCOUT and BRUTE add variety.
_ARCHETYPES: dict[EnemyArchetype, EnemyStats] = {
    EnemyArchetype.BANDIT: EnemyStats(
        speed_base=200.0,
        speed_per_level=2.0,
        health_base=10.0,
        health_per_level=1.0,
        damage=1.0,
        targeting_range=200.0,
        scale=1.0,
        tint=None,
        loot=[
            (ItemKind.HEALTH, 0.1),
            (ItemKind.LIMBS, 0.1),
            (ItemKind.GOLD, 1.0),
        ],
    ),
    # Glass cannon: fast, fragile, sees the player from further away, low reward.
    EnemyArchetype.SCOUT: EnemyStats(
        speed_base=330.0,
        speed_per_level=3.0,
        health_base=5.0,
        health_per_level=1.0,
        damage=1.0,
        targeting_range=260.0,
        scale=0.8,
        tint=(120, 220, 255),
        loot=[
            (ItemKind.GOLD, 1.0),
        ],
    ),
    # Tank: slow, lots of HP, hits hard, drops two coins.
    EnemyArchetype.BRUTE: EnemyStats(
        speed_base=120.0,
        speed_per_level=1.0,
        health_base=28.0,
        health_per_level=3.0,
        damage=2.0,
        targeting_range=200.0,
        scale=1.5,
        tint=(255, 110, 90),
        loot=[
            (ItemKind.HEALTH, 0.2),
            (ItemKind.LIMBS, 0.2),
            (ItemKind.GOLD, 1.0),
            (ItemKind.GOLD, 1.0),
        ],
    ),
}

# Built once per archetype and reused for every spawn (and across esper worlds).
# AnimationProc only reads clip frames/duration/loop and never mutates them, while
# per-entity timing lives in AnimationRuntime, so sharing the surfaces is safe and
# avoids reloading 36 PNGs from disk on every single spawn.
_clip_cache: dict[EnemyArchetype, dict[str, AnimationClip]] = {}


def _transform_frame(
    frame: pygame.Surface, scale: float, tint: tuple[int, int, int] | None
) -> pygame.Surface:
    if scale != 1.0:
        frame = pygame.transform.scale_by(frame, scale)
    if tint is not None:
        frame = frame.copy()
        frame.fill((*tint, 255), special_flags=pygame.BLEND_RGB_MULT)
    return frame


def _build_clips(stats: EnemyStats) -> dict[str, AnimationClip]:
    clips: dict[str, AnimationClip] = {}
    for direction in _DIRECTIONS:
        frames = [
            _transform_frame(
                pygame.image.load(
                    _RUN_PATH.format(direction=direction, i=i)
                ).convert_alpha(),
                stats.scale,
                stats.tint,
            )
            for i in range(1, _RUN_FRAME_COUNT + 1)
        ]
        clips[f"run_{direction}"] = AnimationClip(
            frames=frames, frame_duration=0.08, loop=True
        )
    return clips


def _get_clips(
    archetype: EnemyArchetype, stats: EnemyStats
) -> dict[str, AnimationClip]:
    cached = _clip_cache.get(archetype)
    if cached is None:
        cached = _build_clips(stats)
        _clip_cache[archetype] = cached
    return cached


def create_enemy(
    pos: Position,
    archetype: EnemyArchetype = EnemyArchetype.BANDIT,
    difficulty: int = 0,
) -> int:
    stats = _ARCHETYPES[archetype]
    clips = _get_clips(archetype, stats)

    surface = clips["run_down"].frames[0]
    true_rect = surface.get_bounding_rect()
    offset_x = (true_rect.x + true_rect.width / 2) - surface.get_width() / 2
    offset_y = (true_rect.y + true_rect.height / 2) - surface.get_height() / 2

    return esper.create_entity(
        pos,
        Velocity(0, 0),
        Speed(stats.speed_base + difficulty * stats.speed_per_level),
        Health(
            stats.health_base + difficulty * stats.health_per_level,
            stats.health_base + difficulty * stats.health_per_level,
        ),
        DamageDealer(amount=stats.damage),
        Sprite(surface),
        Hitbox(
            width=true_rect.width,
            height=true_rect.height,
            offset_x=offset_x,
            offset_y=offset_y,
        ),
        EnemyTag(),
        AI(),
        Targeting(range=stats.targeting_range),
        PatrolSettings.from_random(),
        PatrolRuntime(),
        LootTable(LootTableKind.LOOT_MANY, list(stats.loot)),
        AnimationSet(clips=clips),
        AnimationState(current="run_down"),
        AnimationRuntime(state="run_down", frame_index=0, frame_time=0.0),
        DirectionalAnimation(
            idle_prefix="idle",
            move_prefix="run",
            last_direction="down",
            speed_threshold=0.01,
        ),
    )
