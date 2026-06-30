import random
from collections.abc import Callable
from functools import partial
from typing import cast, final, override

import pygame

from client.component import ItemKind
from client.core import Engine
from client.factory import Offer, OfferCategory, ShopContext, draft, eligible_offers
from client.ui.components import NEON_PURPLE, Button

from .scene import Scene

_GOLD = pygame.Color(255, 215, 0)
_WHITE = pygame.Color(255, 255, 255)
_GRAY = pygame.Color(160, 160, 180)
_BORDER = pygame.Color(106, 79, 207)
_RED = pygame.Color(200, 70, 70)
_GREEN = pygame.Color(120, 210, 120)

_CATEGORY_LABEL: dict[OfferCategory, str] = {
    OfferCategory.PERK: "Amélioration",
    OfferCategory.WEAPON: "Arme",
    OfferCategory.OBJECT: "Objet",
}
_CATEGORY_COLOR: dict[OfferCategory, pygame.Color] = {
    OfferCategory.PERK: pygame.Color(160, 125, 255),
    OfferCategory.WEAPON: _GOLD,
    OfferCategory.OBJECT: _GREEN,
}

_DRAFT_SIZE = 3
_REROLL_BASE = 3
_REROLL_GROWTH = 2


@final
class ShopScene(Scene):
    def __init__(
        self,
        engine: Engine,
        ctx: ShopContext,
        on_win: Callable[[], None],
    ):
        super().__init__()
        self._engine = engine
        self._screen = engine.screen
        self._ctx = ctx
        self._on_win = on_win
        self._rerolls = 0
        self._offers: list[Offer | None] = list(draft(ctx, _DRAFT_SIZE))

        w, h = self._screen.get_size()
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
            for i in range(_DRAFT_SIZE)
        ]
        self._btn_reroll = Button(
            "Relancer", NEON_PURPLE, 16, 10, 8, 18, on_click=self._reroll
        )
        self._btn_win = Button(
            "VICTOIRE - 100 pièces", NEON_PURPLE, 20, 14, 10, 22, on_click=self._buy_win
        )

    def _gold(self) -> int:
        return self._ctx.inv.count(ItemKind.GOLD)

    def _reroll_cost(self) -> int:
        return _REROLL_BASE + _REROLL_GROWTH * self._rerolls

    def _reroll(self) -> None:
        cost = self._reroll_cost()
        if self._gold() < cost:
            return
        self._ctx.inv.counts[ItemKind.GOLD] = self._gold() - cost
        self._rerolls += 1
        self._offers = list(draft(self._ctx, _DRAFT_SIZE))

    def _buy(self, i: int) -> None:
        if i >= len(self._offers):
            return
        offer = self._offers[i]
        if offer is None:
            return
        cost = offer.cost(self._ctx)
        if self._gold() < cost:
            return
        self._ctx.inv.counts[ItemKind.GOLD] = self._gold() - cost
        offer.apply(self._ctx)
        self._ctx.counts[offer.id] = self._ctx.counts.get(offer.id, 0) + 1
        if not offer.repeatable:
            self._offers[i] = self._replacement(offer)

    def _replacement(self, sold: Offer) -> Offer | None:
        """Pick a fresh eligible offer not already on display (or None)."""
        shown = {o.id for o in self._offers if o is not None and o.id != sold.id}
        pool = [o for o in eligible_offers(self._ctx) if o.id not in shown]
        return random.choice(pool) if pool else None

    def _buy_win(self) -> None:
        if self._gold() < 100:
            return
        self._ctx.inv.counts[ItemKind.GOLD] = self._gold() - 100
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
        offer: Offer | None,
        btn: Button,
        dt: float,
        events: list[pygame.event.Event],
    ) -> None:
        cx = x + cw // 2
        card_surf = pygame.Surface((cw, ch), pygame.SRCALPHA)
        card_surf.fill((20, 15, 40, 230))
        border = _CATEGORY_COLOR[offer.category] if offer is not None else _BORDER
        pygame.draw.rect(
            card_surf, border, card_surf.get_rect(), width=2, border_radius=12
        )
        self._screen.blit(card_surf, (x, y))

        if offer is None:
            empty = self._font_small.render("—", True, _GRAY)
            self._screen.blit(empty, empty.get_rect(center=(cx, y + ch // 2)))
            return

        tag = self._font_small.render(
            _CATEGORY_LABEL[offer.category], True, _CATEGORY_COLOR[offer.category]
        )
        self._screen.blit(tag, tag.get_rect(centerx=cx, top=y + 12))

        name_s = self._font_name.render(offer.name, True, _WHITE)
        self._screen.blit(name_s, name_s.get_rect(centerx=cx, top=y + 36))

        desc_s = self._font_small.render(offer.desc, True, _GRAY)
        self._screen.blit(desc_s, desc_s.get_rect(centerx=cx, top=y + 72))

        if offer.repeatable:
            count = self._ctx.counts.get(offer.id, 0)
            mid = self._font_small.render(f"Acheté : {count}×", True, _GRAY)
            self._screen.blit(mid, mid.get_rect(centerx=cx, top=y + 98))

        gold = self._gold()
        cost = offer.cost(self._ctx)
        cost_s = self._font_name.render(
            f"{cost} pièces", True, _GOLD if gold >= cost else _RED
        )
        self._screen.blit(cost_s, cost_s.get_rect(centerx=cx, top=y + 122))

        btn.enabled = gold >= cost
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

        title_s = self._font_title.render("BOUTIQUE", True, _WHITE)
        self._screen.blit(title_s, title_s.get_rect(center=(w // 2, 56)))

        gold = self._gold()
        gold_s = self._font_gold.render(f"Or : {gold}", True, _GOLD)
        self._screen.blit(gold_s, gold_s.get_rect(center=(w // 2, 108)))

        # Single row of draft cards
        card_top = 160
        card_h = 320
        card_w = (w - 160 - 40) // _DRAFT_SIZE
        for i in range(_DRAFT_SIZE):
            x = 80 + i * (card_w + 20)
            offer = self._offers[i] if i < len(self._offers) else None
            self._draw_card(
                x, card_top, card_w, card_h, offer, self._btns[i], dt, events
            )

        # Reroll button under the cards
        reroll_cost = self._reroll_cost()
        self._btn_reroll.text = f"Relancer ({reroll_cost})"
        self._btn_reroll.enabled = gold >= reroll_cost
        self._btn_reroll.set_rect(w // 2, card_top + card_h + 24)
        self._btn_reroll.update(dt, events)
        self._btn_reroll.draw(self._screen)

        # Win button (wide, bottom)
        self._btn_win.enabled = gold >= 100
        self._btn_win.rect.width = w - 160
        self._btn_win.rect.height = 64
        self._btn_win.set_rect(w // 2, h - 64 - 20)
        self._btn_win.update(dt, events)
        self._btn_win.draw(self._screen)

        hint_s = self._font_hint.render(
            "E — Fermer  ·  1-4 — Changer d'arme", True, _GRAY
        )
        self._screen.blit(hint_s, hint_s.get_rect(centerx=w // 2, bottom=h - 6))

        return False
