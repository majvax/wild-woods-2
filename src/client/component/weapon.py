from dataclasses import dataclass

@dataclass
class Weapon:
    cooldown_max : float
    bullet_speed : float
    damage : float
    
    cooldown_current : float = 0.0
