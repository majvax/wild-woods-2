from dataclasses import dataclass


@dataclass
class Health:
    max: float
    current: float


@dataclass
class DamageDealer:
    amount: float


@dataclass
class Invincibility:
    time: float
