from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PlayerTag: ...


@dataclass(frozen=True, slots=True)
class EnemyTag: ...


@dataclass(frozen=True, slots=True)
class ProjectileTag: ...


@dataclass(frozen=True, slots=True)
class CampfireTag: ...
