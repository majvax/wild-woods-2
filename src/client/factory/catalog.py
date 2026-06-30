import random
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import IntEnum, auto

from client.component import (
    Arsenal,
    Aura,
    Dash,
    Health,
    Inventory,
    ObjectKind,
    Objects,
    Perks,
    Speed,
    Weapon,
    WeaponKind,
)
from client.factory.weapon import (
    WEAPON_INFO,
    unlock_weapon,
    upgrade_cadence,
    upgrade_damage,
)


class OfferCategory(IntEnum):
    PERK = auto()
    WEAPON = auto()
    OBJECT = auto()


@dataclass
class ShopContext:
    """Live component references bundled by the game scene for the shop.

    The shop runs in its own esper world, so it only mutates these references
    in place (never adds/removes components on the player entity).
    """

    inv: Inventory
    hp: Health
    speed: Speed
    weapon: Weapon
    arsenal: Arsenal
    dash: Dash
    perks: Perks
    objects: Objects
    aura: Aura
    counts: dict[str, int] = field(default_factory=dict)


@dataclass(frozen=True)
class Offer:
    id: str
    category: OfferCategory
    name: str
    desc: str
    base_cost: int
    apply: Callable[[ShopContext], None]
    growth: int = 0
    repeatable: bool = False
    available: Callable[[ShopContext], bool] = lambda ctx: True

    def cost(self, ctx: ShopContext) -> int:
        return self.base_cost + self.growth * ctx.counts.get(self.id, 0)


def _perk(
    id: str,
    name: str,
    desc: str,
    base: int,
    growth: int,
    apply: Callable[[ShopContext], None],
) -> Offer:
    return Offer(
        id=id,
        category=OfferCategory.PERK,
        name=name,
        desc=desc,
        base_cost=base,
        growth=growth,
        repeatable=True,
        apply=apply,
    )


def _add_hp(ctx: ShopContext) -> None:
    ctx.hp.max += 1
    ctx.hp.current += 1


def _add_speed(ctx: ShopContext) -> None:
    ctx.speed.value *= 1.12


def _add_crit(ctx: ShopContext) -> None:
    ctx.perks.crit_chance = min(1.0, ctx.perks.crit_chance + 0.08)


def _add_crit_dmg(ctx: ShopContext) -> None:
    ctx.perks.crit_mult += 0.25


def _add_lifesteal(ctx: ShopContext) -> None:
    ctx.perks.lifesteal = min(1.0, ctx.perks.lifesteal + 0.1)


def _reduce_dash_cd(ctx: ShopContext) -> None:
    ctx.dash.cooldown = max(0.3, ctx.dash.cooldown * 0.85)


def _enable_pierce(ctx: ShopContext) -> None:
    ctx.perks.pierce = True


def _buy_onion(ctx: ShopContext) -> None:
    ctx.objects.owned.add(ObjectKind.ONION)
    ctx.aura.active = True
    ctx.aura.radius = 120.0
    ctx.aura.damage_frac = 0.3
    ctx.aura.cooldown = 0.5


def _weapon_offer(kind: WeaponKind) -> Offer:
    info = WEAPON_INFO[kind]
    return Offer(
        id=f"weapon_{kind.name}",
        category=OfferCategory.WEAPON,
        name=info.name,
        desc=info.desc,
        base_cost=info.price,
        apply=lambda ctx: unlock_weapon(ctx.weapon, ctx.arsenal, kind),
        available=lambda ctx: kind not in ctx.arsenal.owned,
    )


CATALOG: list[Offer] = [
    # Repeatable perks
    _perk(
        "dmg",
        "Dégâts +25%",
        "+25% dégâts (toutes armes)",
        4,
        2,
        lambda ctx: upgrade_damage(ctx.weapon, ctx.arsenal),
    ),
    _perk(
        "cadence",
        "Cadence +10%",
        "−10% délai de tir (toutes armes)",
        4,
        2,
        lambda ctx: upgrade_cadence(ctx.weapon, ctx.arsenal),
    ),
    _perk("hp", "Vie +1", "+1 PV maximum", 5, 1, _add_hp),
    _perk("speed", "Célérité +12%", "+12% vitesse de déplacement", 4, 2, _add_speed),
    _perk("crit", "Coup critique +8%", "+8% de chance de critique", 5, 2, _add_crit),
    _perk(
        "crit_dmg",
        "Dégâts critiques +25%",
        "+25% dégâts des coups critiques",
        5,
        2,
        _add_crit_dmg,
    ),
    _perk(
        "lifesteal",
        "Vol de vie +10%",
        "+10% de soin à l'élimination",
        6,
        2,
        _add_lifesteal,
    ),
    _perk(
        "dash_cd", "Roulade −15%", "−15% recharge de l'esquive", 5, 2, _reduce_dash_cd
    ),
    # One-time perk
    Offer(
        id="pierce",
        category=OfferCategory.PERK,
        name="Perforation",
        desc="Tous les tirs transpercent",
        base_cost=25,
        apply=_enable_pierce,
        available=lambda ctx: not ctx.perks.pierce,
    ),
    # Objects (one-time)
    Offer(
        id="onion",
        category=OfferCategory.OBJECT,
        name="Oignon",
        desc="Aura infligeant des dégâts aux ennemis proches",
        base_cost=35,
        apply=_buy_onion,
        available=lambda ctx: ObjectKind.ONION not in ctx.objects.owned,
    ),
    # Weapons (one-time)
    _weapon_offer(WeaponKind.SHOTGUN),
    _weapon_offer(WeaponKind.SMG),
    _weapon_offer(WeaponKind.SNIPER),
]


def eligible_offers(ctx: ShopContext) -> list[Offer]:
    return [
        o
        for o in CATALOG
        if o.available(ctx) and (o.repeatable or ctx.counts.get(o.id, 0) == 0)
    ]


def draft(ctx: ShopContext, n: int = 3) -> list[Offer]:
    """Pick up to ``n`` distinct currently-eligible offers at random."""
    pool = eligible_offers(ctx)
    return random.sample(pool, min(n, len(pool)))
