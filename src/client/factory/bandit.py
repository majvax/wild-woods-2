import esper
import pygame

from client.component import (
    AI,
    DamageDealer,
    EnemyTag,
    Health,
    ItemKind,
    LootTable,
    LootTableKind,
    PatrolRuntime,
    PatrolSettings,
    Position,
    Speed,
    Sprite,
    Targeting,
    Velocity,
    Hitbox,
)


def create_bandit(pos: Position):
    # TODO: replace with actual bandit sprite
    surface = pygame.image.load("sprite/ennemis/perso_079.png").convert_alpha()
    entries = [
        (ItemKind.SYRINGE, 0.5),
        (ItemKind.POTION, 0.3),
        (ItemKind.GOLD, 0.2),
    ]

    true_rect = surface.get_bounding_rect()
    offset_x = (true_rect.x + true_rect.width / 2) - surface.get_width() / 2
    offset_y = (true_rect.y + true_rect.height / 2) - surface.get_height() / 2

    esper.create_entity(
        pos,
        Velocity(0, 0),
        Speed(200),
        Health(20, 20),
        DamageDealer(amount=1.0),
        Sprite(surface),
        Hitbox(
            width=true_rect.width,
            height=true_rect.height,
            offset_x=offset_x,
            offset_y=offset_y,
        ),
        EnemyTag(),
        AI(),
        Targeting(range=200),
        PatrolSettings.from_random(),
        PatrolRuntime(),
        LootTable(LootTableKind.LOOT_ONE, entries),
    )
