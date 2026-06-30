from dataclasses import dataclass


@dataclass
class Dash:
    """Player dash/dodge ability.

    Tuning fields (``speed``/``duration``/``cooldown``) describe the move; the
    remaining fields are runtime state mutated by ``DashProc``.
    """

    speed: float = 1200.0  # burst speed while dashing (player base Speed is 300)
    duration: float = 0.16  # active dash window in seconds (~192px of travel)
    cooldown: float = 1.5  # seconds before the next dash is available
    active_time: float = 0.0  # remaining active dash time
    cooldown_time: float = 0.0  # remaining cooldown
    dir_x: float = 0.0  # locked dash direction (unit vector)
    dir_y: float = 0.0
