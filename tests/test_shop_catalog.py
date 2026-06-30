import uuid

import esper
import pytest

from client.component import (
    Arsenal,
    Aura,
    Dash,
    Health,
    Inventory,
    ItemKind,
    Objects,
    Perks,
    Speed,
    WeaponKind,
)
from client.factory import ShopContext, draft, eligible_offers
from client.factory.catalog import CATALOG
from client.factory.weapon import build_weapon


def _ctx(gold: int = 0) -> ShopContext:
    inv = Inventory()
    if gold:
        inv.add(ItemKind.GOLD, gold)
    return ShopContext(
        inv=inv,
        hp=Health(10, 10),
        speed=Speed(300),
        weapon=build_weapon(WeaponKind.PISTOL),
        arsenal=Arsenal(owned={WeaponKind.PISTOL}, active=WeaponKind.PISTOL),
        dash=Dash(),
        perks=Perks(),
        objects=Objects(),
        aura=Aura(),
        counts={},
    )


def _offer(offer_id: str):
    return next(o for o in CATALOG if o.id == offer_id)


# --- catalog / draft -------------------------------------------------------


def test_offer_cost_scales_with_counts():
    ctx = _ctx()
    dmg = _offer("dmg")
    assert dmg.cost(ctx) == dmg.base_cost
    ctx.counts["dmg"] = 2
    assert dmg.cost(ctx) == dmg.base_cost + 2 * dmg.growth


def test_one_time_offer_unavailable_after_purchase():
    ctx = _ctx()
    onion = _offer("onion")
    assert onion.available(ctx) is True
    onion.apply(ctx)
    assert onion.available(ctx) is False
    assert onion not in eligible_offers(ctx)


def test_weapon_offer_excluded_once_owned():
    ctx = _ctx()
    shotgun = _offer("weapon_SHOTGUN")
    assert shotgun.available(ctx) is True
    shotgun.apply(ctx)
    assert WeaponKind.SHOTGUN in ctx.arsenal.owned
    assert shotgun.available(ctx) is False


def test_draft_returns_distinct_eligible_offers():
    ctx = _ctx()
    offers = draft(ctx, 3)
    assert len(offers) == 3
    ids = [o.id for o in offers]
    assert len(set(ids)) == 3
    eligible_ids = {o.id for o in eligible_offers(ctx)}
    assert all(i in eligible_ids for i in ids)


def test_apply_is_world_safe():
    """Purchase effects only mutate refs, so they work in any esper world."""
    ctx = _ctx()
    world = uuid.uuid4().hex
    esper.switch_world(world)
    try:
        _offer("onion").apply(ctx)  # would crash if it touched esper
        _offer("weapon_SNIPER").apply(ctx)
    finally:
        esper.switch_world("default")
        esper.delete_world(world)
    assert ctx.aura.active is True
    assert WeaponKind.SNIPER in ctx.arsenal.owned


# --- perk applies ----------------------------------------------------------


def test_perk_damage_applies_global_multiplier():
    ctx = _ctx()
    base = ctx.weapon.damage
    _offer("dmg").apply(ctx)
    assert ctx.arsenal.damage_mult == pytest.approx(1.25)
    assert ctx.weapon.damage == max(1, round(base * 1.25))


def test_perk_speed_applies():
    ctx = _ctx()
    _offer("speed").apply(ctx)
    assert ctx.speed.value == pytest.approx(300 * 1.12)


def test_perk_hp_applies():
    ctx = _ctx()
    _offer("hp").apply(ctx)
    assert ctx.hp.max == 11
    assert ctx.hp.current == 11


def test_perk_crit_and_dash_and_pierce_apply():
    ctx = _ctx()
    _offer("crit").apply(ctx)
    assert ctx.perks.crit_chance == pytest.approx(0.08)

    before = ctx.dash.cooldown
    _offer("dash_cd").apply(ctx)
    assert ctx.dash.cooldown == pytest.approx(before * 0.85)

    pierce = _offer("pierce")
    assert pierce.available(ctx) is True
    pierce.apply(ctx)
    assert ctx.perks.pierce is True
    assert pierce.available(ctx) is False
