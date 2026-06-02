from collections.abc import Sequence
from typing import final, override

import esper
from esper import Processor

from client.component import (
    CampfireTag,
    EnemyTag,
    Hitbox,
    PlayerTag,
    Position,
    hitbox_bounds,
)


def _resolve_against_campfires(
    movables: Sequence[tuple[int, tuple[object, Position, Hitbox]]],
    campfires: Sequence[tuple[int, tuple[object, Position, Hitbox]]],
) -> None:
    for _, (_, m_pos, m_hit) in movables:
        for _, (_, c_pos, c_hit) in campfires:
            ml, mt, mr, mb = hitbox_bounds(m_pos, m_hit)
            cl, ct, cr, cb = hitbox_bounds(c_pos, c_hit)

            ox = min(mr, cr) - max(ml, cl)
            oy = min(mb, cb) - max(mt, ct)
            if ox <= 0 or oy <= 0:
                continue

            if ox < oy:
                m_pos.x += ox if m_pos.x > c_pos.x + c_hit.offset_x else -ox
            else:
                m_pos.y += oy if m_pos.y > c_pos.y + c_hit.offset_y else -oy


@final
class CollisionProc(Processor):
    @override
    def process(self, dt: float) -> None:
        campfires = esper.get_components(CampfireTag, Position, Hitbox)
        if not campfires:
            return

        _resolve_against_campfires(
            esper.get_components(PlayerTag, Position, Hitbox), campfires
        )
        _resolve_against_campfires(
            esper.get_components(EnemyTag, Position, Hitbox), campfires
        )
