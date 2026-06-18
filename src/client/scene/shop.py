from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from typing import cast, final, override

import pygame

from client.component import Health, Inventory, ItemKind, Weapon
from client.core import Engine
from client.ui.components import NEON_PURPLE, Button

from .scene import Scene

_GOLD = pygame.Color(255, 215, 0)
_WHITE = pygame.Color(255, 255, 255)
_GRAY = pygame.Color(160, 160, 180)
_BORDER = pygame.Color(106, 79, 207)
_RED = pygame.Color(200, 70, 70)


@dataclass
class _Upgrade:
    label: str
    desc: str
    base_cost: int
    increment: int
    count: int = field(default=0)

    def cost(self) -> int:
        return self.base_cost + self.count * self.increment


@final
class ShopScene(Scene):
    def __init__(
        self,
        engine: Engine,
        hp: Health,
        weapon: Weapon,
        inv: Inventory,
        on_win: Callable[[], None],
        purchase_counts: list[int],
    ):
        super().__init__()
        self._engine = engine
        self._screen = engine.screen
        self._hp = hp
        self._weapon = weapon
        self._inv = inv
        self._on_win = on_win
        self._purchase_counts = purchase_counts

        self._upgrades = [
            _Upgrade("+1 Vie", "Augmente les PV max de 1", 5, 1, purchase_counts[0]),
            _Upgrade(
                "Cadence +10%",
                "Réduit le délai de tir de 10%",
                2,
                2,
                purchase_counts[1],
            ),
            _Upgrade(
                "Dégâts +25%", "Augmente les dégâts de 25%", 2, 1, purchase_counts[2]
            ),
        ]

        w, h = self._screen.get_size()

        # Capture the rendered game frame — push happens after esper.process so it's fresh
        self._bg = engine.screen.copy()

        self._overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        self._overlay.fill((10, 5, 20, 160))

        self._font_title = pygame.font.SysFont("Arial", 52, bold=True)
        self._font_name = pygame.font.SysFont("Arial", 22, bold=True)
        self._font_small = pygame.font.SysFont("Arial", 15)
        self._font_gold = pygame.font.SysFont("Arial", 24, bold=True)
        self._font_hint = pygame.font.SysFont("Arial", 14)

        self._btns = [
            Button("Acheter", NEON_PURPLE, 14, 8, 8, 18, on_click=partial(self._buy, i))
            for i in range(3)
        ]

        self._btn_win = Button(
            "VICTOIRE - 100 pièces",
            NEON_PURPLE,
            20,
            14,
            10,
            22,
            on_click=self._buy_win,
        )
        self._btn_win.rect.width = w - 160
        self._btn_win.rect.height = 70

    def _buy(self, i: int) -> None:
        upg = self._upgrades[i]
        gold = self._inv.count(ItemKind.GOLD)
        if gold < upg.cost():
            return
        self._inv.counts[ItemKind.GOLD] = gold - upg.cost()
        upg.count += 1
        self._purchase_counts[i] = upg.count
        if i == 0:
            self._hp.max += 1
            self._hp.current += 1
        elif i == 1:
            self._weapon.cooldown_max = max(0.05, self._weapon.cooldown_max * 0.9)
        else:
            self._weapon.damage = max(1, int(self._weapon.damage * 1.25))

    def _buy_win(self) -> None:
        gold = self._inv.count(ItemKind.GOLD)
        if gold < 100:
            return
        self._inv.counts[ItemKind.GOLD] = gold - 100
        self._on_win()

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        w, h = self._screen.get_size()

        for event in events:
            if event.type == pygame.KEYDOWN and cast(int, event.key) == pygame.K_e:
                self._engine.sm.pop()
                return False

        self._screen.blit(self._bg, (0, 0))
        self._screen.blit(self._overlay, (0, 0))

        # Title
        title_s = self._font_title.render("BOUTIQUE", True, _WHITE)
        self._screen.blit(title_s, title_s.get_rect(center=(w // 2, 60)))

        # Gold
        gold = self._inv.count(ItemKind.GOLD)
        gold_s = self._font_gold.render(f"Or : {gold}", True, _GOLD)
        self._screen.blit(gold_s, gold_s.get_rect(center=(w // 2, 115)))

        # Layout zones
        win_h = 100
        win_top = h - win_h - 20
        card_top = 150
        card_h = win_top - card_top - 20
        card_w = (w - 160 - 40) // 3  # 3 cards, 2 gaps of 20

        for i, (upg, btn) in enumerate(zip(self._upgrades, self._btns)):
            x = 80 + i * (card_w + 20)
            cx = x + card_w // 2

            # Card background
            card_surf = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
            card_surf.fill((20, 15, 40, 230))
            pygame.draw.rect(
                card_surf, _BORDER, card_surf.get_rect(), width=2, border_radius=12
            )
            self._screen.blit(card_surf, (x, card_top))

            # Name
            name_s = self._font_name.render(upg.label, True, _WHITE)
            self._screen.blit(name_s, name_s.get_rect(centerx=cx, top=card_top + 22))

            # Description
            desc_s = self._font_small.render(upg.desc, True, _GRAY)
            self._screen.blit(desc_s, desc_s.get_rect(centerx=cx, top=card_top + 60))

            # Purchase count
            count_s = self._font_small.render(f"Acheté : {upg.count}×", True, _GRAY)
            self._screen.blit(count_s, count_s.get_rect(centerx=cx, top=card_top + 85))

            # Cost (colored by affordability)
            cost = upg.cost()
            cost_s = self._font_name.render(
                f"{cost} pièces", True, _GOLD if gold >= cost else _RED
            )
            self._screen.blit(cost_s, cost_s.get_rect(centerx=cx, top=card_top + 118))

            # Buy button
            btn.enabled = gold >= cost
            btn.set_rect(cx, card_top + card_h - btn.rect.height - 20)
            btn.update(dt, events)
            btn.draw(self._screen)

        # Win button (wide, bottom)
        self._btn_win.enabled = gold >= 100
        self._btn_win.rect.width = w - 160
        self._btn_win.set_rect(w // 2, win_top)
        self._btn_win.update(dt, events)
        self._btn_win.draw(self._screen)

        # Close hint
        hint_s = self._font_hint.render("E — Fermer la boutique", True, _GRAY)
        self._screen.blit(hint_s, hint_s.get_rect(centerx=w // 2, bottom=h - 6))

        return False
