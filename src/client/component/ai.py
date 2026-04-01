import random
from dataclasses import dataclass
from enum import IntEnum, auto
from typing import Self


class AIState(IntEnum):
    IDLE = auto()
    PATROL = auto()
    CHASE = auto()
    ATTACK = auto()
    DEAD = auto()


@dataclass
class AI:
    state: AIState = AIState.IDLE


@dataclass
class PatrolRuntime:
    timer: float = 0.0
    direction: tuple[float, float] = (0.0, 0.0)


@dataclass
class PatrolSettings:
    radius: float
    idle_chance: float
    min_time: float
    max_time: float

    @classmethod
    def from_random(cls) -> Self:
        return cls(
            radius=random.uniform(50, 200),
            idle_chance=random.uniform(0.1, 0.7),
            min_time=random.uniform(0.5, 1.0),
            max_time=random.uniform(1.5, 3.0),
        )
