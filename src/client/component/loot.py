from dataclasses import dataclass, field
from enum import IntEnum, auto


class ItemKind(IntEnum):
    HEALTH = auto()
    LIMBS = auto()
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


@dataclass
class Inventory:
    counts: dict[ItemKind, int] = field(default_factory=dict)

    def add(self, kind: ItemKind, amount: int = 1) -> None:
        self.counts[kind] = self.counts.get(kind, 0) + amount

    def count(self, kind: ItemKind) -> int:
        return self.counts.get(kind, 0)
