import uuid

import esper
import pygame
import pytest

from client.component.ai import AI, PatrolRuntime, PatrolSettings
from client.component.gameplay import Sprite
from client.component.loot import ItemKind, ItemTag, LootTable
from client.component.physics import Position, Speed, Velocity
from client.component.tags import EnemyTag, PlayerTag
from client.component.targeting import Targeting
from client.factory.bandit import create_bandit
from client.factory.item import _ITEM_SIZES, create_item
from client.factory.player import create_player


@pytest.fixture
def esper_world():
    world_id = uuid.uuid4().hex
    esper.switch_world(world_id)
    yield world_id
    esper.switch_world("default")
    esper.delete_world(world_id)


class DummyImage:
    def convert_alpha(self) -> pygame.Surface:
        return pygame.Surface((10, 10), pygame.SRCALPHA)


def test_create_item_adds_components(esper_world):
    create_item(Position(1, 2), ItemKind.GOLD)

    entities = list(esper.get_components(Position, Sprite, ItemTag))
    assert len(entities) == 1
    _, (pos, sprite, tag) = entities[0]

    assert (pos.x, pos.y) == (1, 2)
    assert tag.kind == ItemKind.GOLD
    assert sprite.surface.get_size() == _ITEM_SIZES[ItemKind.GOLD]


def test_create_player_adds_components(esper_world, monkeypatch):
    monkeypatch.setattr(pygame.image, "load", lambda _: DummyImage())

    create_player(Position(3, 4))

    entities = list(esper.get_components(PlayerTag, Position, Velocity, Speed))
    assert len(entities) == 1
    ent, (tag, pos, vel, speed) = entities[0]
    sprite = esper.component_for_entity(ent, Sprite)

    assert isinstance(tag, PlayerTag)
    assert (pos.x, pos.y) == (3, 4)
    assert (vel.vx, vel.vy) == (0, 0)
    assert speed.value == 300
    assert sprite.surface.get_size() == (10, 10)


def test_create_bandit_adds_components(esper_world, monkeypatch):
    monkeypatch.setattr(pygame.image, "load", lambda _: DummyImage())

    create_bandit(Position(5, 6))

    entities = list(esper.get_components(EnemyTag, Position, Velocity, Speed))
    assert len(entities) == 1
    ent_id, (tag, pos, vel, speed) = entities[0]

    sprite = esper.component_for_entity(ent_id, Sprite)
    ai = esper.component_for_entity(ent_id, AI)
    targeting = esper.component_for_entity(ent_id, Targeting)
    settings = esper.component_for_entity(ent_id, PatrolSettings)
    runtime = esper.component_for_entity(ent_id, PatrolRuntime)
    loot = esper.component_for_entity(ent_id, LootTable)

    assert isinstance(tag, EnemyTag)
    assert (pos.x, pos.y) == (5, 6)
    assert (vel.vx, vel.vy) == (0, 0)
    assert speed.value == 200
    assert isinstance(sprite, Sprite)
    assert isinstance(ai, AI)
    assert targeting.range == 200
    assert targeting.atk_range == 50
    assert isinstance(settings, PatrolSettings)
    assert isinstance(runtime, PatrolRuntime)
    assert len(loot.entries) == 3
