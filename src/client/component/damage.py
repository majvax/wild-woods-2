from dataclasses import dataclass


@dataclass
class Health:
    max: int
    current: int


@dataclass
class DamageDealer:
    amount: float


@dataclass
class Invincibility:
    time: float
