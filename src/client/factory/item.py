import esper
import pygame

from client.component.gameplay import Sprite
from client.component.loot import ItemKind, ItemTag
from client.component.physics import Position

_ITEM_COLORS: dict[ItemKind, str] = {
    ItemKind.SYRINGE: "#00e5ff",
    ItemKind.POTION: "#ff00e5",
    ItemKind.GOLD: "#ffde00",
}

_ITEM_SIZES: dict[ItemKind, tuple[int, int]] = {
    ItemKind.SYRINGE: (6, 18),
    ItemKind.POTION: (10, 14),
    ItemKind.GOLD: (18, 8),
}


def create_item(pos: Position, kind: ItemKind) -> None:
    w, h = _ITEM_SIZES[kind]
    surface = pygame.Surface((w, h))
    surface.fill(_ITEM_COLORS[kind])
    esper.create_entity(Position(pos.x, pos.y), Sprite(surface), ItemTag(kind))
