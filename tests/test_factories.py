import uuid

import esper
import pygame
import pytest

from client.component import (
    AI,
    EnemyTag,
    ItemKind,
    ItemTag,
    LootTable,
    PatrolRuntime,
    PatrolSettings,
    PlayerTag,
    Position,
    Speed,
    Sprite,
    Targeting,
    Velocity,
)
from client.factory import create_bandit, create_item, create_player


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
    assert isinstance(settings, PatrolSettings)
    assert isinstance(runtime, PatrolRuntime)
    assert len(loot.entries) == 3
