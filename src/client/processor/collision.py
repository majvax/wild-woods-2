from typing import final, override

import esper
from esper import Processor

from client.component import CampfireTag, Hitbox, PlayerTag, Position


def _bounds(pos: Position, hit: Hitbox) -> tuple[float, float, float, float]:
    cx = pos.x + hit.offset_x
    cy = pos.y + hit.offset_y
    return (
        cx - hit.width / 2,
        cy - hit.height / 2,
        cx + hit.width / 2,
        cy + hit.height / 2,
    )


@final
class CollisionProc(Processor):
    @override
    def process(self, dt: float) -> None:
        players = esper.get_components(PlayerTag, Position, Hitbox)
        campfires = esper.get_components(CampfireTag, Position, Hitbox)
        if not players or not campfires:
            return

        for _, (_, p_pos, p_hit) in players:
            for _, (_, c_pos, c_hit) in campfires:
                pl, pt, pr, pb = _bounds(p_pos, p_hit)
                cl, ct, cr, cb = _bounds(c_pos, c_hit)

                ox = min(pr, cr) - max(pl, cl)
                oy = min(pb, cb) - max(pt, ct)
                if ox <= 0 or oy <= 0:
                    continue

                if ox < oy:
                    p_pos.x += ox if p_pos.x > c_pos.x + c_hit.offset_x else -ox
                else:
                    p_pos.y += oy if p_pos.y > c_pos.y + c_hit.offset_y else -oy
