import esper
import pygame

from client.component import ItemKind, ItemTag, Position, Sprite

ITEM_SPRITE_PATHS: dict[ItemKind, str] = {
    ItemKind.GOLD: "assets/sprite/icons/coin.png",
    ItemKind.HEALTH: "assets/sprite/icons/hearth.png",
    ItemKind.LIMBS: "assets/sprite/icons/limbs.png",
}

_ITEM_DROP_SIZE = 20


def create_item(pos: Position, kind: ItemKind) -> None:
    raw = pygame.image.load(ITEM_SPRITE_PATHS[kind]).convert_alpha()
    surface = pygame.transform.scale(raw, (_ITEM_DROP_SIZE, _ITEM_DROP_SIZE))
    esper.create_entity(Position(pos.x, pos.y), Sprite(surface), ItemTag(kind))
