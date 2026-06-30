from dataclasses import dataclass, replace

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
    """Return a fresh Weapon instance for the given kind (base stats)."""
    return replace(WEAPON_INFO[kind].template)


def apply_weapon(weapon: Weapon, arsenal: Arsenal, kind: WeaponKind) -> None:
    """Reconfigure ``weapon`` in place to ``kind``, applying global upgrades.

    The player keeps a single Weapon component; switching weapons mutates it
    instead of swapping components, so this works regardless of which esper
    world is active (the shop runs in its own world). Global damage/cadence
    multipliers live on the arsenal and are re-derived from the template here,
    so upgrades apply to every weapon and the result is idempotent.
    """
    tpl = WEAPON_INFO[kind].template
    weapon.kind = kind
    weapon.bullet_speed = tpl.bullet_speed
    weapon.pellets = tpl.pellets
    weapon.spread = tpl.spread
    weapon.pierce = tpl.pierce
    weapon.projectile_lifetime = tpl.projectile_lifetime
    weapon.cooldown_max = max(0.05, tpl.cooldown_max * arsenal.cooldown_mult)
    weapon.damage = max(1, round(tpl.damage * arsenal.damage_mult))
    weapon.cooldown_current = 0.0


def equip_weapon(weapon: Weapon, arsenal: Arsenal, kind: WeaponKind) -> bool:
    """Make ``kind`` active if owned and not already active. True on switch."""
    if kind not in arsenal.owned or arsenal.active == kind:
        return False
    arsenal.active = kind
    apply_weapon(weapon, arsenal, kind)
    return True


def unlock_weapon(weapon: Weapon, arsenal: Arsenal, kind: WeaponKind) -> None:
    """Add ``kind`` to the arsenal and equip it (no gold handling)."""
    arsenal.owned.add(kind)
    arsenal.active = kind
    apply_weapon(weapon, arsenal, kind)


def buy_weapon(
    weapon: Weapon, arsenal: Arsenal, inv: Inventory, kind: WeaponKind
) -> bool:
    """Unlock and equip ``kind`` if affordable and not already owned."""
    if kind in arsenal.owned:
        return False
    price = WEAPON_INFO[kind].price
    if inv.count(ItemKind.GOLD) < price:
        return False
    inv.counts[ItemKind.GOLD] = inv.count(ItemKind.GOLD) - price
    unlock_weapon(weapon, arsenal, kind)
    return True


def upgrade_cadence(weapon: Weapon, arsenal: Arsenal) -> None:
    """Global fire-rate upgrade: -10% cooldown on all weapons."""
    arsenal.cooldown_mult *= 0.9
    apply_weapon(weapon, arsenal, arsenal.active)


def upgrade_damage(weapon: Weapon, arsenal: Arsenal) -> None:
    """Global damage upgrade: +25% damage on all weapons."""
    arsenal.damage_mult *= 1.25
    apply_weapon(weapon, arsenal, arsenal.active)
