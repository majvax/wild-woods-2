import esper
import pygame

from client.component import (
    AnimationClip,
    AnimationRuntime,
    AnimationSet,
    AnimationState,
    CampfireTag,
    Health,
    Hitbox,
    Position,
    Sprite,
)


def create_campfire(pos: Position, max_health: float = 100.0) -> None:
    basic_frames = [
        pygame.image.load(f"assets/sprite/campfire/basic/frame{i}.png").convert_alpha()
        for i in range(1, 6)
    ]
    low_frames = [
        pygame.image.load(
            f"assets/sprite/campfire/low-life/fire-low{i}.png"
        ).convert_alpha()
        for i in range(1, 4)
    ]
    clips = {
        "basic": AnimationClip(frames=basic_frames, frame_duration=0.15, loop=True),
        "low-life": AnimationClip(frames=low_frames, frame_duration=0.15, loop=True),
    }
    surface = basic_frames[0]
    true_rect = surface.get_bounding_rect()
    esper.create_entity(
        pos,
        Sprite(surface),
        AnimationSet(clips=clips),
        AnimationState(current="basic"),
        AnimationRuntime(state="basic", frame_index=0, frame_time=0.0),
        Health(max=max_health, current=max_health),
        Hitbox(
            width=true_rect.width,
            height=true_rect.height - 160,
            offset_x=(true_rect.x + true_rect.width / 2) - surface.get_width() / 2,
            offset_y=80
            + (true_rect.y + true_rect.height / 2)
            - surface.get_height() / 2,
        ),
        CampfireTag(),
    )
