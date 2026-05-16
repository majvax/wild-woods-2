from dataclasses import dataclass

import pygame


@dataclass
class Sprite:
    surface: pygame.Surface


@dataclass
class AnimationClip:
    frames: list[pygame.Surface]
    frame_duration: float
    loop: bool = True


@dataclass
class AnimationSet:
    clips: dict[str, AnimationClip]


@dataclass
class AnimationState:
    current: str


@dataclass
class AnimationRuntime:
    state: str
    frame_index: int
    frame_time: float


@dataclass
class DirectionalAnimation:
    idle_prefix: str
    move_prefix: str
    last_direction: str
    speed_threshold: float


@dataclass
class Lifetime:
    time: float
