import math
import uuid

import esper
import pygame
import pytest

from client.component import (
    AI,
    AIState,
    CampfireTag,
    EnemyTag,
    Hitbox,
    ItemKind,
    LootTable,
    LootTableKind,
    PlayerTag,
    Position,
    Speed,
    Targeting,
    Velocity,
)
from client.processor import (
    BrainProc,
    InputProc,
    LootProc,
    MovementProc,
    TargetingProc,
)


@pytest.fixture
def esper_world():
    world_id = uuid.uuid4().hex
    esper.switch_world(world_id)
    yield world_id
    esper.switch_world("default")
    esper.delete_world(world_id)


def test_targeting_proc_sets_target_when_in_range(esper_world):
    player_id = esper.create_entity(PlayerTag(), Position(10, 10))
    enemy_id = esper.create_entity(EnemyTag(), Position(12, 10), Targeting(range=5))

    TargetingProc().process(0.016)

    targeting = esper.component_for_entity(enemy_id, Targeting)
    assert targeting.target == player_id
    assert targeting.distance == pytest.approx(2.0)


def test_targeting_proc_clears_target_when_out_of_range(esper_world):
    player_id = esper.create_entity(PlayerTag(), Position(0, 0))
    enemy_id = esper.create_entity(EnemyTag(), Position(50, 0), Targeting(range=5))

    TargetingProc().process(0.016)

    targeting = esper.component_for_entity(enemy_id, Targeting)
    assert targeting.target is None
    assert targeting.distance == float("inf")


def test_brain_proc_chase_moves_toward_target(esper_world):
    target_id = esper.create_entity(Position(10, 0))
    enemy_id = esper.create_entity(
        AI(),
        Targeting(range=200, distance=100, target=target_id),
        Position(0, 0),
        Velocity(0, 0),
        Speed(100),
    )

    BrainProc().process(0.016)

    ai = esper.component_for_entity(enemy_id, AI)
    vel = esper.component_for_entity(enemy_id, Velocity)
    assert ai.state == AIState.CHASE
    assert vel.vx > 0
    assert vel.vy == pytest.approx(0.0)


def test_brain_proc_patrol_seeks_campfire(esper_world):
    esper.create_entity(CampfireTag(), Position(100, 0), Hitbox(width=32, height=32))

    enemy_id = esper.create_entity(
        AI(),
        Targeting(range=200, distance=float("inf"), target=None),
        Position(0, 0),
        Velocity(0, 0),
        Speed(100),
    )

    BrainProc().process(0.016)

    ai = esper.component_for_entity(enemy_id, AI)
    vel = esper.component_for_entity(enemy_id, Velocity)
    assert ai.state == AIState.PATROL
    assert vel.vx == pytest.approx(20.0)
    assert vel.vy == pytest.approx(0.0)


def test_loot_proc_loot_one_spawns_item(esper_world, monkeypatch):
    pressed = [False] * 1024
    pressed[pygame.K_l] = True
    monkeypatch.setattr(pygame.key, "get_just_pressed", lambda: pressed)

    created: list[tuple[Position, ItemKind]] = []

    def fake_create_item(pos: Position, kind: ItemKind) -> None:
        created.append((pos, kind))

    monkeypatch.setattr("client.processor.loot.create_item", fake_create_item)
    monkeypatch.setattr("client.processor.loot.random.randint", lambda a, b: 0)

    esper.create_entity(
        Position(5, 6),
        LootTable(LootTableKind.LOOT_ONE, [(ItemKind.GOLD, 1.0)]),
    )

    LootProc().process(0.016)

    assert created == [(Position(5, 6), ItemKind.GOLD)]


def test_loot_proc_key_not_pressed_does_nothing(esper_world, monkeypatch):
    pressed = [False] * 1024
    monkeypatch.setattr(pygame.key, "get_just_pressed", lambda: pressed)

    created: list[tuple[Position, ItemKind]] = []

    def fake_create_item(pos: Position, kind: ItemKind) -> None:
        created.append((pos, kind))

    monkeypatch.setattr("client.processor.loot.create_item", fake_create_item)

    esper.create_entity(
        Position(5, 6),
        LootTable(LootTableKind.LOOT_ONE, [(ItemKind.GOLD, 1.0)]),
    )

    LootProc().process(0.016)

    assert created == []


def test_loot_proc_loot_one_empty_entries(esper_world, monkeypatch):
    pressed = [False] * 1024
    pressed[pygame.K_l] = True
    monkeypatch.setattr(pygame.key, "get_just_pressed", lambda: pressed)

    created: list[tuple[Position, ItemKind]] = []

    def fake_create_item(pos: Position, kind: ItemKind) -> None:
        created.append((pos, kind))

    monkeypatch.setattr("client.processor.loot.create_item", fake_create_item)

    esper.create_entity(
        Position(5, 6),
        LootTable(LootTableKind.LOOT_ONE, []),
    )

    LootProc().process(0.016)

    assert created == []


def test_loot_proc_loot_many_spawns_items(esper_world, monkeypatch):
    pressed = [False] * 1024
    pressed[pygame.K_l] = True
    monkeypatch.setattr(pygame.key, "get_just_pressed", lambda: pressed)

    created: list[tuple[Position, ItemKind]] = []

    def fake_create_item(pos: Position, kind: ItemKind) -> None:
        created.append((pos, kind))

    monkeypatch.setattr("client.processor.loot.create_item", fake_create_item)
    monkeypatch.setattr("client.processor.loot.random.random", lambda: 0.0)

    esper.create_entity(
        Position(1, 2),
        LootTable(
            LootTableKind.LOOT_MANY,
            [(ItemKind.HEALTH, 0.5), (ItemKind.LIMBS, 0.5)],
        ),
    )

    LootProc().process(0.016)

    assert created == [
        (Position(1, 2), ItemKind.HEALTH),
        (Position(1, 2), ItemKind.LIMBS),
    ]


def test_brain_proc_attack_when_in_range(esper_world):
    target_id = esper.create_entity(Position(0, 0), Hitbox(width=10, height=10))
    enemy_id = esper.create_entity(
        AI(AIState.CHASE),
        Targeting(range=200, distance=10, target=target_id),
        Position(0, 0),
        Velocity(5, 5),
        Speed(100),
        Hitbox(width=10, height=10),
    )

    BrainProc().process(0.016)

    ai = esper.component_for_entity(enemy_id, AI)
    vel = esper.component_for_entity(enemy_id, Velocity)
    assert ai.state == AIState.ATTACK
    assert vel.vx == 0.0
    assert vel.vy == 0.0


def test_brain_proc_attack_to_chase_when_out_of_range(esper_world):
    target_id = esper.create_entity(Position(100, 0), Hitbox(width=10, height=10))
    enemy_id = esper.create_entity(
        AI(AIState.ATTACK),
        Targeting(range=200, distance=100, target=target_id),
        Position(0, 0),
        Velocity(0, 0),
        Speed(100),
        Hitbox(width=10, height=10),
    )

    BrainProc().process(0.016)

    ai = esper.component_for_entity(enemy_id, AI)
    vel = esper.component_for_entity(enemy_id, Velocity)
    assert ai.state == AIState.CHASE
    assert vel.vx > 0


def test_brain_proc_chase_zero_distance(esper_world):
    target_id = esper.create_entity(Position(0, 0), Hitbox(width=10, height=10))
    enemy_id = esper.create_entity(
        AI(AIState.CHASE),
        Targeting(range=200, distance=0, target=target_id),
        Position(0, 0),
        Velocity(1, 1),
        Speed(100),
        Hitbox(width=10, height=10),
    )

    BrainProc().process(0.016)

    vel = esper.component_for_entity(enemy_id, Velocity)
    assert vel.vx == 0.0
    assert vel.vy == 0.0


def test_input_proc_normalizes_diagonal(esper_world, monkeypatch):
    keys = [False] * 1024
    keys[pygame.K_z] = True
    keys[pygame.K_d] = True
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: keys)

    ent = esper.create_entity(Velocity(0, 0), Speed(100), PlayerTag())

    InputProc().process(0.016)

    vel = esper.component_for_entity(ent, Velocity)
    expected = 100 / math.sqrt(2)
    assert vel.vx == pytest.approx(expected)
    assert vel.vy == pytest.approx(-expected)


def test_movement_proc_updates_position(esper_world):
    ent = esper.create_entity(Position(1, 2), Velocity(10, -5))

    MovementProc().process(0.5)

    pos = esper.component_for_entity(ent, Position)
    assert pos.x == pytest.approx(6.0)
    assert pos.y == pytest.approx(-0.5)
