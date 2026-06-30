import uuid

import esper
import pygame
import pytest

from client.component import (
    Arsenal,
    Aura,
    DamageDealer,
    EnemyTag,
    Health,
    Hitbox,
    Inventory,
    Invincibility,
    Perks,
    Piercing,
    PlayerTag,
    Position,
    ProjectileTag,
    Speed,
    Velocity,
    WeaponKind,
)
from client.factory.weapon import build_weapon
from client.processor import AuraProc, DamageProc, ShootingProc, SpatialGridProc


@pytest.fixture
def esper_world():
    world_id = uuid.uuid4().hex
    esper.switch_world(world_id)
    yield world_id
    esper.switch_world("default")
    esper.delete_world(world_id)


def _make_player(
    perks: Perks | None = None,
    hp: Health | None = None,
    aura: Aura | None = None,
) -> int:
    return esper.create_entity(
        PlayerTag(),
        Position(0, 0),
        Velocity(0, 0),
        Speed(300),
        hp if hp is not None else Health(10, 10),
        Inventory(),
        Hitbox(width=10, height=10),
        Invincibility(0),
        perks if perks is not None else Perks(),
        build_weapon(WeaponKind.PISTOL),
        Arsenal(owned={WeaponKind.PISTOL}, active=WeaponKind.PISTOL),
        aura if aura is not None else Aura(),
    )


def _silence_mixer(monkeypatch) -> None:
    monkeypatch.setattr(
        pygame.mixer, "Sound", lambda _: type("S", (), {"play": lambda self: None})()
    )


# --- crit / lifesteal ------------------------------------------------------


def test_crit_multiplies_projectile_damage(esper_world, monkeypatch):
    _silence_mixer(monkeypatch)
    monkeypatch.setattr("client.processor.combat.random.random", lambda: 0.0)

    _make_player(perks=Perks(crit_chance=1.0, crit_mult=3.0))
    enemy = esper.create_entity(
        EnemyTag(), Position(0, 0), Health(100, 100), Hitbox(width=10, height=10)
    )
    esper.create_entity(
        ProjectileTag(),
        Position(0, 0),
        Velocity(0, 0),
        DamageDealer(amount=10.0),
        Hitbox(width=10, height=10),
    )

    SpatialGridProc().process(0.016)
    DamageProc().process(0.016)

    assert esper.component_for_entity(enemy, Health).current == pytest.approx(70.0)


def test_lifesteal_heals_player_on_kill(esper_world, monkeypatch):
    _silence_mixer(monkeypatch)
    monkeypatch.setattr("client.processor.combat.random.random", lambda: 0.0)

    player = _make_player(perks=Perks(lifesteal=1.0), hp=Health(10, 5))
    esper.create_entity(
        EnemyTag(), Position(0, 0), Health(5, 5), Hitbox(width=10, height=10)
    )
    esper.create_entity(
        ProjectileTag(),
        Position(0, 0),
        Velocity(0, 0),
        DamageDealer(amount=10.0),
        Hitbox(width=10, height=10),
    )

    SpatialGridProc().process(0.016)
    DamageProc().process(0.016)

    assert esper.component_for_entity(player, Health).current == 6


# --- Perforation perk ------------------------------------------------------


def test_pierce_perk_makes_shots_pierce(esper_world, monkeypatch):
    surface = pygame.Surface((800, 600))
    monkeypatch.setattr(pygame.display, "get_surface", lambda: surface)
    monkeypatch.setattr(pygame.mouse, "get_pressed", lambda: (True, False, False))
    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: (600, 300))
    calls: list[bool] = []
    monkeypatch.setattr(
        "client.processor.shooting.create_projectile",
        lambda *a, **k: calls.append(k.get("pierce", False)),
    )

    _make_player(perks=Perks(pierce=True))  # pistol normally does not pierce

    ShootingProc().process(0.016)

    assert calls == [True]


# --- Onion aura ------------------------------------------------------------


def test_aura_damages_enemies_in_radius(esper_world, monkeypatch):
    monkeypatch.setattr("client.processor.combat.random.random", lambda: 1.0)  # no crit

    _make_player(
        aura=Aura(active=True, radius=50.0, damage_frac=0.5, cooldown=0.5, timer=0.0)
    )
    inside = esper.create_entity(
        EnemyTag(), Position(30, 0), Health(100, 100), Hitbox(width=10, height=10)
    )
    outside = esper.create_entity(
        EnemyTag(), Position(300, 0), Health(100, 100), Hitbox(width=10, height=10)
    )

    SpatialGridProc().process(0.5)
    AuraProc().process(0.5)

    # base = 0.5 * pistol damage (10) = 5
    assert esper.component_for_entity(inside, Health).current == pytest.approx(95.0)
    assert esper.component_for_entity(outside, Health).current == 100


def test_inactive_aura_does_nothing(esper_world):
    _make_player(aura=Aura(active=False, radius=50.0, timer=0.0))
    enemy = esper.create_entity(
        EnemyTag(), Position(10, 0), Health(100, 100), Hitbox(width=10, height=10)
    )

    SpatialGridProc().process(0.5)
    AuraProc().process(0.5)

    assert esper.component_for_entity(enemy, Health).current == 100


def test_aura_respects_cooldown(esper_world, monkeypatch):
    monkeypatch.setattr("client.processor.combat.random.random", lambda: 1.0)

    _make_player(
        aura=Aura(active=True, radius=50.0, damage_frac=0.5, cooldown=0.5, timer=0.0)
    )
    enemy = esper.create_entity(
        EnemyTag(), Position(20, 0), Health(100, 100), Hitbox(width=10, height=10)
    )

    SpatialGridProc().process(0.1)
    AuraProc().process(0.1)  # first tick fires, resets timer to 0.5
    after_first = esper.component_for_entity(enemy, Health).current
    AuraProc().process(0.1)  # timer 0.4 > 0 -> no tick
    after_second = esper.component_for_entity(enemy, Health).current

    assert after_first == pytest.approx(95.0)
    assert after_second == after_first


def test_piercing_unaffected_enemy_not_double_hit(esper_world, monkeypatch):
    """Sanity: piercing still records hits with the new crit path."""
    _silence_mixer(monkeypatch)
    monkeypatch.setattr("client.processor.combat.random.random", lambda: 1.0)

    _make_player()
    enemy = esper.create_entity(
        EnemyTag(), Position(0, 0), Health(100, 100), Hitbox(width=10, height=10)
    )
    esper.create_entity(
        ProjectileTag(),
        Position(0, 0),
        Velocity(0, 0),
        DamageDealer(amount=10.0),
        Hitbox(width=10, height=10),
        Piercing(),
    )

    proc = DamageProc()
    SpatialGridProc().process(0.016)
    proc.process(0.016)
    SpatialGridProc().process(0.016)
    proc.process(0.016)

    assert esper.component_for_entity(enemy, Health).current == pytest.approx(90.0)
