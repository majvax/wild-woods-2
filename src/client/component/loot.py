from dataclasses import dataclass, field
from enum import IntEnum, auto


class ItemKind(IntEnum):
    SYRINGE = auto()
    POTION = auto()
    GOLD = auto()


class LootTableKind(IntEnum):
    LOOT_ONE = auto()
    LOOT_MANY = auto()


@dataclass
class LootTable:
    kind: LootTableKind
    entries: list[tuple[ItemKind, float]] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ItemTag:
    kind: ItemKind
