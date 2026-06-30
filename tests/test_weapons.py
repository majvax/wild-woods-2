import uuid

import esper
import pygame
import pytest

from client.component import (
    Arsenal,
    DamageDealer,
    EnemyTag,
    Health,
    Hitbox,
    Inventory,
    Invincibility,
    ItemKind,
    Piercing,
    PlayerTag,
    Position,
    ProjectileTag,
    Speed,
    Velocity,
    Weapon,
    WeaponKind,
)
from client.factory import build_weapon, buy_weapon, equip_weapon
from client.factory.weapon import WEAPON_INFO
from client.processor import DamageProc, ShootingProc, SpatialGridProc


@pytest.fixture
def esper_world():
    world_id = uuid.uuid4().hex
    esper.switch_world(world_id)
    yield world_id
    esper.switch_world("default")
    esper.delete_world(world_id)


def _make_player_with(arsenal: Arsenal, gold: int = 0) -> int:
    inv = Inventory()
    if gold:
        inv.add(ItemKind.GOLD, gold)
    ent = esper.create_entity(
        PlayerTag(),
        Position(0, 0),
        Velocity(0, 0),
        Speed(300),
        Health(10, 10),
        inv,
        Hitbox(width=10, height=10),
        Invincibility(0),
        arsenal,
        arsenal.owned[arsenal.active],
    )
    return ent


# --- weapon builder / arsenal helpers -------------------------------------


def test_build_weapon_sets_kind_and_is_fresh_instance():
    a = build_weapon(WeaponKind.SHOTGUN)
    b = build_weapon(WeaponKind.SHOTGUN)
    assert a.kind == WeaponKind.SHOTGUN
    assert a.pellets == 5
    assert a is not b  # separate instances so upgrades don't leak


def test_equip_weapon_switches_active_and_component(esper_world):
    pistol = build_weapon(WeaponKind.PISTOL)
    arsenal = Arsenal(owned={WeaponKind.PISTOL: pistol}, active=WeaponKind.PISTOL)
    ent = _make_player_with(arsenal)
    arsenal.owned[WeaponKind.SMG] = build_weapon(WeaponKind.SMG)

    assert equip_weapon(ent, arsenal, WeaponKind.SMG) is True
    assert arsenal.active == WeaponKind.SMG
    assert esper.component_for_entity(ent, Weapon).kind == WeaponKind.SMG
    # Re-equipping the already-active weapon is a no-op.
    assert equip_weapon(ent, arsenal, WeaponKind.SMG) is False
    # Equipping an unowned weapon fails.
    assert equip_weapon(ent, arsenal, WeaponKind.SNIPER) is False


def test_buy_weapon_deducts_gold_and_equips(esper_world):
    pistol = build_weapon(WeaponKind.PISTOL)
    arsenal = Arsenal(owned={WeaponKind.PISTOL: pistol}, active=WeaponKind.PISTOL)
    price = WEAPON_INFO[WeaponKind.SHOTGUN].price
    ent = _make_player_with(arsenal, gold=price + 5)
    inv = esper.component_for_entity(ent, Inventory)

    assert buy_weapon(ent, arsenal, inv, WeaponKind.SHOTGUN) is True
    assert WeaponKind.SHOTGUN in arsenal.owned
    assert arsenal.active == WeaponKind.SHOTGUN
    assert inv.count(ItemKind.GOLD) == 5
    # Buying again does nothing (already owned).
    assert buy_weapon(ent, arsenal, inv, WeaponKind.SHOTGUN) is False


def test_buy_weapon_rejected_when_too_poor(esper_world):
    pistol = build_weapon(WeaponKind.PISTOL)
    arsenal = Arsenal(owned={WeaponKind.PISTOL: pistol}, active=WeaponKind.PISTOL)
    ent = _make_player_with(arsenal, gold=0)
    inv = esper.component_for_entity(ent, Inventory)

    assert buy_weapon(ent, arsenal, inv, WeaponKind.SNIPER) is False
    assert WeaponKind.SNIPER not in arsenal.owned
    assert inv.count(ItemKind.GOLD) == 0


# --- shot geometry --------------------------------------------------------


def test_shot_angles_single_is_exact_when_no_spread():
    assert ShootingProc._shot_angles(1.0, 1, 0.0) == [1.0]


def test_shot_angles_shotgun_fans_evenly():
    angles = ShootingProc._shot_angles(0.0, 5, 0.5)
    assert len(angles) == 5
    assert angles[0] == pytest.approx(-0.25)
    assert angles[-1] == pytest.approx(0.25)
    assert angles[2] == pytest.approx(0.0)  # centred


# --- ShootingProc integration --------------------------------------------


def _arm_mouse(monkeypatch) -> None:
    surface = pygame.Surface((800, 600))
    monkeypatch.setattr(pygame.display, "get_surface", lambda: surface)
    monkeypatch.setattr(pygame.mouse, "get_pressed", lambda: (True, False, False))
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (600, 300))


def test_shooting_proc_shotgun_fires_all_pellets(esper_world, monkeypatch):
    _arm_mouse(monkeypatch)
    calls: list[bool] = []
    monkeypatch.setattr(
        "client.processor.shooting.create_projectile",
        lambda *a, **k: calls.append(k.get("pierce", False)),
    )

    arsenal = Arsenal(
        owned={WeaponKind.SHOTGUN: build_weapon(WeaponKind.SHOTGUN)},
        active=WeaponKind.SHOTGUN,
    )
    _make_player_with(arsenal)

    ShootingProc().process(0.016)

    assert len(calls) == 5
    assert all(p is False for p in calls)


def test_shooting_proc_sniper_fires_one_piercing(esper_world, monkeypatch):
    _arm_mouse(monkeypatch)
    calls: list[bool] = []
    monkeypatch.setattr(
        "client.processor.shooting.create_projectile",
        lambda *a, **k: calls.append(k.get("pierce", False)),
    )

    arsenal = Arsenal(
        owned={WeaponKind.SNIPER: build_weapon(WeaponKind.SNIPER)},
        active=WeaponKind.SNIPER,
    )
    _make_player_with(arsenal)

    ShootingProc().process(0.016)

    assert calls == [True]


# --- piercing damage ------------------------------------------------------


def test_piercing_projectile_hits_each_enemy_once_without_dying(
    esper_world, monkeypatch
):
    monkeypatch.setattr(
        pygame.mixer, "Sound", lambda _: type("S", (), {"play": lambda self: None})()
    )

    # Player required by DamageProc (it queries PlayerView each frame).
    pistol = build_weapon(WeaponKind.PISTOL)
    _make_player_with(
        Arsenal(owned={WeaponKind.PISTOL: pistol}, active=WeaponKind.PISTOL)
    )

    bullet = esper.create_entity(
        ProjectileTag(),
        Position(100, 100),
        Velocity(0, 0),
        DamageDealer(amount=5.0),
        Hitbox(width=10, height=10),
        Piercing(),
    )
    e1 = esper.create_entity(
        EnemyTag(), Position(100, 100), Health(20, 20), Hitbox(width=10, height=10)
    )
    e2 = esper.create_entity(
        EnemyTag(), Position(102, 100), Health(20, 20), Hitbox(width=10, height=10)
    )

    proc = DamageProc()
    SpatialGridProc().process(0.016)
    proc.process(0.016)
    SpatialGridProc().process(0.016)
    proc.process(0.016)

    assert esper.entity_exists(bullet)  # piercing round survives
    assert esper.component_for_entity(e1, Health).current == 15  # hit once only
    assert esper.component_for_entity(e2, Health).current == 15
