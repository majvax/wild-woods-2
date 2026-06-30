import math
from typing import final, override

import esper
from esper import Processor

from client.component import Aura, EnemyTag, Health, Hitbox, Perks, Position
from client.core.spatial import get_active_grid
from client.processor.combat import apply_lifesteal, roll_damage
from client.view.player import PlayerView


@final
class AuraProc(Processor):
    """The Onion object: periodically damages enemies around the player.

    Runs after DamageProc. The Aura component is pre-attached (inactive) to the
    player; the shop turns it on, so this never needs structural esper changes.
    """

    @override
    def process(self, dt: float):
        player = PlayerView.get()
        try:
            aura = esper.component_for_entity(player.ent, Aura)
        except KeyError:
            return
        if not aura.active:
            return

        aura.timer -= dt
        if aura.timer > 0:
            return
        aura.timer = aura.cooldown

        weapon = player.weapon()
        if weapon is None:
            return
        try:
            perks = esper.component_for_entity(player.ent, Perks)
        except KeyError:
            perks = None

        base = aura.damage_frac * weapon.damage
        r = aura.radius
        bounds = (
            player.pos.x - r,
            player.pos.y - r,
            player.pos.x + r,
            player.pos.y + r,
        )
        seen: set[int] = set()
        for ent in get_active_grid().query_aabb(*bounds):
            if ent == player.ent or ent in seen:
                continue
            seen.add(ent)
            try:
                ehp = esper.component_for_entity(ent, Health)
                epos = esper.component_for_entity(ent, Position)
                esper.component_for_entity(ent, EnemyTag)
                esper.component_for_entity(ent, Hitbox)
            except KeyError:
                continue

            if math.hypot(epos.x - player.pos.x, epos.y - player.pos.y) > r:
                continue

            ehp.current -= roll_damage(base, perks)
            if ehp.current <= 0:
                apply_lifesteal(perks, player.hp)
