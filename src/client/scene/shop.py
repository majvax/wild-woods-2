from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from typing import cast, final, override

import pygame

from client.component import Arsenal, Health, Inventory, ItemKind, Weapon, WeaponKind
from client.core import Engine
from client.factory import WEAPON_INFO, WEAPON_ORDER, buy_weapon, equip_weapon
from client.ui.components import NEON_PURPLE, Button

from .scene import Scene

_GOLD = pygame.Color(255, 215, 0)
_WHITE = pygame.Color(255, 255, 255)
_GRAY = pygame.Color(160, 160, 180)
_BORDER = pygame.Color(106, 79, 207)
_ACTIVE_BORDER = pygame.Color(160, 125, 255)
_RED = pygame.Color(200, 70, 70)
_GREEN = pygame.Color(120, 210, 120)


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
        arsenal: Arsenal,
        player_ent: int,
    ):
        super().__init__()
        self._engine = engine
        self._screen = engine.screen
        self._hp = hp
        self._weapon = weapon
        self._inv = inv
        self._on_win = on_win
        self._purchase_counts = purchase_counts
        self._arsenal = arsenal
        self._player_ent = player_ent

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

        # Weapons that can be unlocked (the pistol is free / always owned).
        self._weapon_kinds = [k for k in WEAPON_ORDER if WEAPON_INFO[k].price > 0]

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
        # Sized to the widest label; text/action set per frame in _draw_weapon_card.
        self._weapon_btns = [
            Button("Acheter (00)", NEON_PURPLE, 14, 8, 8, 18)
            for _ in self._weapon_kinds
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

    def _active_weapon(self) -> Weapon:
        return self._arsenal.owned[self._arsenal.active]

    def _buy(self, i: int) -> None:
        upg = self._upgrades[i]
        gold = self._inv.count(ItemKind.GOLD)
        if gold < upg.cost():
            return
        self._inv.counts[ItemKind.GOLD] = gold - upg.cost()
        upg.count += 1
        self._purchase_counts[i] = upg.count
        weapon = self._active_weapon()
        if i == 0:
            self._hp.max += 1
            self._hp.current += 1
        elif i == 1:
            weapon.cooldown_max = max(0.05, weapon.cooldown_max * 0.9)
        else:
            weapon.damage = max(1, int(weapon.damage * 1.25))

    def _weapon_click(self, kind: WeaponKind) -> None:
        if kind in self._arsenal.owned:
            equip_weapon(self._player_ent, self._arsenal, kind)
        else:
            buy_weapon(self._player_ent, self._arsenal, self._inv, kind)

    def _buy_win(self) -> None:
        gold = self._inv.count(ItemKind.GOLD)
        if gold < 100:
            return
        self._inv.counts[ItemKind.GOLD] = gold - 100
        self._on_win()

    @override
    def on_enter(self) -> None:
        pass

    def _draw_card(
        self,
        x: int,
        y: int,
        cw: int,
        ch: int,
        title: str,
        desc: str,
        mid: str,
        bottom: str,
        bottom_color: pygame.Color,
        btn: Button,
        dt: float,
        events: list[pygame.event.Event],
        active: bool = False,
    ) -> None:
        cx = x + cw // 2
        card_surf = pygame.Surface((cw, ch), pygame.SRCALPHA)
        card_surf.fill((20, 15, 40, 230))
        pygame.draw.rect(
            card_surf,
            _ACTIVE_BORDER if active else _BORDER,
            card_surf.get_rect(),
            width=3 if active else 2,
            border_radius=12,
        )
        self._screen.blit(card_surf, (x, y))

        name_s = self._font_name.render(title, True, _WHITE)
        self._screen.blit(name_s, name_s.get_rect(centerx=cx, top=y + 16))

        desc_s = self._font_small.render(desc, True, _GRAY)
        self._screen.blit(desc_s, desc_s.get_rect(centerx=cx, top=y + 50))

        mid_s = self._font_small.render(mid, True, _GRAY)
        self._screen.blit(mid_s, mid_s.get_rect(centerx=cx, top=y + 74))

        bottom_s = self._font_name.render(bottom, True, bottom_color)
        self._screen.blit(bottom_s, bottom_s.get_rect(centerx=cx, top=y + 100))

        btn.set_rect(cx, y + ch - btn.rect.height - 18)
        btn.update(dt, events)
        btn.draw(self._screen)

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
        self._screen.blit(title_s, title_s.get_rect(center=(w // 2, 56)))

        # Gold + currently equipped weapon
        gold = self._inv.count(ItemKind.GOLD)
        gold_s = self._font_gold.render(f"Or : {gold}", True, _GOLD)
        self._screen.blit(gold_s, gold_s.get_rect(center=(w // 2, 104)))
        active_name = WEAPON_INFO[self._arsenal.active].name
        arme_s = self._font_small.render(f"Arme : {active_name}", True, _GRAY)
        self._screen.blit(arme_s, arme_s.get_rect(center=(w // 2, 130)))

        # Layout: two rows of three cards between the header and the win button.
        win_h = 70
        win_top = h - win_h - 20
        content_top = 150
        content_bottom = win_top - 20
        row_gap = 16
        row_h = (content_bottom - content_top - row_gap) // 2
        card_w = (w - 160 - 40) // 3

        def card_x(i: int) -> int:
            return 80 + i * (card_w + 20)

        # Row 1: stat upgrades
        for i, (upg, btn) in enumerate(zip(self._upgrades, self._btns)):
            cost = upg.cost()
            btn.enabled = gold >= cost
            self._draw_card(
                card_x(i),
                content_top,
                card_w,
                row_h,
                upg.label,
                upg.desc,
                f"Acheté : {upg.count}×",
                f"{cost} pièces",
                _GOLD if gold >= cost else _RED,
                btn,
                dt,
                events,
            )

        # Row 2: weapons (buy or equip)
        weapons_y = content_top + row_h + row_gap
        for i, (kind, btn) in enumerate(zip(self._weapon_kinds, self._weapon_btns)):
            info = WEAPON_INFO[kind]
            tpl = info.template
            owned = kind in self._arsenal.owned
            active = self._arsenal.active == kind

            if not owned:
                btn.text = f"Acheter ({info.price})"
                btn.enabled = gold >= info.price
                bottom, bottom_color = (
                    f"{info.price} pièces",
                    (_GOLD if gold >= info.price else _RED),
                )
            elif active:
                btn.text = "Équipé"
                btn.enabled = False
                bottom, bottom_color = "Équipé", _GREEN
            else:
                btn.text = "Équiper"
                btn.enabled = True
                bottom, bottom_color = "Possédé", _GREEN
            btn.on_click = partial(self._weapon_click, kind)

            self._draw_card(
                card_x(i),
                weapons_y,
                card_w,
                row_h,
                info.name,
                info.desc,
                f"Dég. {tpl.damage} · Cadence {tpl.cooldown_max:g}s",
                bottom,
                bottom_color,
                btn,
                dt,
                events,
                active=active,
            )

        # Win button (wide, bottom)
        self._btn_win.enabled = gold >= 100
        self._btn_win.rect.width = w - 160
        self._btn_win.set_rect(w // 2, win_top)
        self._btn_win.update(dt, events)
        self._btn_win.draw(self._screen)

        # Close hint
        hint_s = self._font_hint.render(
            "E — Fermer  ·  1-4 — Changer d'arme", True, _GRAY
        )
        self._screen.blit(hint_s, hint_s.get_rect(centerx=w // 2, bottom=h - 6))

        return False
