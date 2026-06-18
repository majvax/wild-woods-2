import esper
import pygame

from client.component import (
    AI,
    AnimationClip,
    AnimationRuntime,
    AnimationSet,
    AnimationState,
    DirectionalAnimation,
    DamageDealer,
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


def _load_sequence(path_template: str, count: int) -> list[pygame.Surface]:
    return [
        pygame.image.load(path_template.format(i=i)).convert_alpha()
        for i in range(1, count + 1)
    ]


def create_bandit(pos: Position, difficulty: int = 0):
    directions = ["up", "down", "left", "right"]
    dir_map = {
        "up": "up",
        "down": "down",
        "left": "left",
        "right": "right",
    }

    clips: dict[str, AnimationClip] = {}
    for direction in directions:
        run_frames = _load_sequence(
            f"assets/sprite/ennemis/run/{dir_map[direction]}/{{i}}.png",
            9,
        )
        clips[f"run_{direction}"] = AnimationClip(
            frames=run_frames, frame_duration=0.08, loop=True
        )

    surface = clips["run_down"].frames[0]
    entries = [
        (ItemKind.HEALTH, 0.5),
        (ItemKind.LIMBS, 0.3),
        (ItemKind.GOLD, 0.2),
    ]

    true_rect = surface.get_bounding_rect()
    offset_x = (true_rect.x + true_rect.width / 2) - surface.get_width() / 2
    offset_y = (true_rect.y + true_rect.height / 2) - surface.get_height() / 2

    esper.create_entity(
        pos,
        Velocity(0, 0),
        Speed(200 + difficulty * 2),
        Health(10 + difficulty, 10 + difficulty),
        DamageDealer(amount=1.0),
        Sprite(surface),
        Hitbox(
            width=true_rect.width,
            height=true_rect.height,
            offset_x=offset_x,
            offset_y=offset_y,
        ),
        EnemyTag(),
        AI(),
        Targeting(range=200),
        PatrolSettings.from_random(),
        PatrolRuntime(),
        LootTable(LootTableKind.LOOT_ONE, entries),
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
