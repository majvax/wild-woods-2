from dataclasses import dataclass, replace

import esper

from client.component import Arsenal, Inventory, ItemKind, Weapon, WeaponKind


@dataclass(frozen=True)
class WeaponInfo:
    name: str
    desc: str
    price: int  # gold cost to unlock in the shop (0 = starting weapon)
    template: Weapon


# Hotkey order: index i is selected with the (i+1) number key.
WEAPON_ORDER: list[WeaponKind] = [
    WeaponKind.PISTOL,
    WeaponKind.SHOTGUN,
    WeaponKind.SMG,
    WeaponKind.SNIPER,
]

WEAPON_INFO: dict[WeaponKind, WeaponInfo] = {
    WeaponKind.PISTOL: WeaponInfo(
        name="Pistolet",
        desc="Tir unique équilibré",
        price=0,
        template=Weapon(
            cooldown_max=0.8,
            bullet_speed=600.0,
            damage=10,
            kind=WeaponKind.PISTOL,
        ),
    ),
    WeaponKind.SHOTGUN: WeaponInfo(
        name="Fusil à pompe",
        desc="5 plombs en cône, courte portée",
        price=30,
        template=Weapon(
            cooldown_max=0.9,
            bullet_speed=550.0,
            damage=6,
            kind=WeaponKind.SHOTGUN,
            pellets=5,
            spread=0.5,
            projectile_lifetime=0.35,
        ),
    ),
    WeaponKind.SMG: WeaponInfo(
        name="Mitraillette",
        desc="Cadence élevée, faibles dégâts",
        price=40,
        template=Weapon(
            cooldown_max=0.12,
            bullet_speed=700.0,
            damage=4,
            kind=WeaponKind.SMG,
            spread=0.12,
            projectile_lifetime=5.0,
        ),
    ),
    WeaponKind.SNIPER: WeaponInfo(
        name="Sniper",
        desc="Perforant, gros dégâts, lent",
        price=50,
        template=Weapon(
            cooldown_max=1.3,
            bullet_speed=1400.0,
            damage=40,
            kind=WeaponKind.SNIPER,
            pierce=True,
            projectile_lifetime=1.5,
        ),
    ),
}


def build_weapon(kind: WeaponKind) -> Weapon:
    """Return a fresh Weapon instance for the given kind."""
    return replace(WEAPON_INFO[kind].template)


def equip_weapon(ent: int, arsenal: Arsenal, kind: WeaponKind) -> bool:
    """Make ``kind`` the active weapon if owned. Returns True on switch."""
    weapon = arsenal.owned.get(kind)
    if weapon is None or arsenal.active == kind:
        return False
    arsenal.active = kind
    esper.add_component(ent, weapon)
    return True


def buy_weapon(ent: int, arsenal: Arsenal, inv: Inventory, kind: WeaponKind) -> bool:
    """Unlock and equip ``kind`` if affordable and not already owned."""
    if kind in arsenal.owned:
        return False
    price = WEAPON_INFO[kind].price
    if inv.count(ItemKind.GOLD) < price:
        return False
    inv.counts[ItemKind.GOLD] = inv.count(ItemKind.GOLD) - price
    arsenal.owned[kind] = build_weapon(kind)
    equip_weapon(ent, arsenal, kind)
    return True
