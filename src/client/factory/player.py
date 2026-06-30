import esper
import pygame

from client.component import (
    AnimationClip,
    AnimationRuntime,
    AnimationSet,
    AnimationState,
    Arsenal,
    Dash,
    DirectionalAnimation,
    Health,
    Hitbox,
    Inventory,
    Invincibility,
    PlayerTag,
    Position,
    Speed,
    Sprite,
    Velocity,
    WeaponKind,
)
from client.factory.weapon import build_weapon


def _load_sequence(path_template: str, count: int) -> list[pygame.Surface]:
    return [
        pygame.image.load(path_template.format(i=i)).convert_alpha()
        for i in range(1, count + 1)
    ]


def create_player(pos: Position, health: int = 5):
    directions = ["up", "down", "left", "right"]
    dir_map = {
        "up": "up",
        "down": "left",
        "left": "down",
        "right": "right",
    }
    clips: dict[str, AnimationClip] = {}
    for direction in directions:
        run_frames = _load_sequence(
            f"assets/sprite/player/run/{dir_map[direction]}/{{i}}.png",
            8,
        )
        idle_frames = _load_sequence(
            f"assets/sprite/player/idle/{dir_map[direction]}/{{i}}.png", 2
        )
        clips[f"run_{direction}"] = AnimationClip(
            frames=run_frames, frame_duration=0.08, loop=True
        )
        clips[f"idle_{direction}"] = AnimationClip(
            frames=idle_frames, frame_duration=0.3, loop=True
        )

    death_frames = _load_sequence("assets/sprite/player/hurt/up/{i}.png", 6)
    clips["death_up"] = AnimationClip(
        frames=death_frames, frame_duration=0.12, loop=False
    )

    surface = clips["idle_down"].frames[0]
    pistolet = build_weapon(WeaponKind.PISTOL)
    arsenal = Arsenal(owned={WeaponKind.PISTOL}, active=WeaponKind.PISTOL)

    true_rect = surface.get_bounding_rect()
    offset_x = (true_rect.x + true_rect.width / 2) - surface.get_width() / 2
    offset_y = (true_rect.y + true_rect.height / 2) - surface.get_height() / 2
    esper.create_entity(
        pos,
        Velocity(0, 0),
        Speed(300),
        Sprite(surface),
        PlayerTag(),
        Health(health, health),
        Invincibility(0),
        Dash(),
        Inventory(),
        Hitbox(
            width=true_rect.width,
            height=true_rect.height,
            offset_x=offset_x,
            offset_y=offset_y,
        ),
        pistolet,
        arsenal,
        AnimationSet(clips=clips),
        AnimationState(current="idle_down"),
        AnimationRuntime(state="idle_down", frame_index=0, frame_time=0.0),
        DirectionalAnimation(
            idle_prefix="idle",
            move_prefix="run",
            last_direction="down",
            speed_threshold=0.01,
        ),
    )
