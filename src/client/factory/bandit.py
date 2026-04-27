import esper
import pygame

from client.component.ai import AI, PatrolRuntime, PatrolSettings
from client.component.gameplay import Sprite
from client.component.loot import ItemKind, LootTable, LootTableKind
from client.component.physics import Position, Speed, Velocity
from client.component.tags import EnemyTag
from client.component.targeting import Targeting


def create_bandit(pos: Position):
    # TODO: replace with actual bandit sprite
    surface = pygame.image.load("sprite/player/standard/hurt/up/6.png").convert_alpha()
    entries = [
        (ItemKind.SYRINGE, 0.5),
        (ItemKind.POTION, 0.3),
        (ItemKind.GOLD, 0.2),
    ]

    esper.create_entity(
        pos,
        Velocity(0, 0),
        Speed(200),
        Sprite(surface),
        EnemyTag(),
        AI(),
        Targeting(range=200, atk_range=50),
        PatrolSettings.from_random(),
        PatrolRuntime(),
        LootTable(LootTableKind.LOOT_ONE, entries),
    )
