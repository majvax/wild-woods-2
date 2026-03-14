from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayerTag: ...


@dataclass(frozen=True, slots=True)
class EnemyTag: ...
