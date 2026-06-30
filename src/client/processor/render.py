from typing import final, override

import esper
import pygame
from esper import Processor

from client.component import (
    CampfireTag,
    Dash,
    Health,
    Hitbox,
    ItemKind,
    ObjectKind,
    Position,
    Sprite,
    EnemyTag,
)
from client.core import TILE_SIZE, get_bg_data
from client.core.engine import Engine
from client.factory import WEAPON_INFO, WEAPON_ORDER
from client.factory.item import ITEM_SPRITE_PATHS
from client.processor.render_helpers import (
    Camera,
    DebugOverlay,
    draw_tiled_background,
)
from client.processor.damage import INVINCIBILITY_AFTER_HIT
from client.view.player import PlayerView

_INVENTORY_ICON_SIZE = 18

_OBJECT_NAMES: dict[ObjectKind, str] = {ObjectKind.ONION: "Oignon"}


@final
class RenderProc(Processor):
    def __init__(self, screen: pygame.Surface, engine: Engine):
        super().__init__()
        self.screen = screen
        self._engine = engine
        self.font = pygame.font.SysFont("Arial", 18)
        self._item_icons: dict[ItemKind, pygame.Surface] = {
            kind: pygame.transform.scale(
                pygame.image.load(path).convert_alpha(),
                (_INVENTORY_ICON_SIZE, _INVENTORY_ICON_SIZE),
            )
            for kind, path in ITEM_SPRITE_PATHS.items()
        }
        self._camera = Camera(smoothness=12.0)
        self._background, _, _ = get_bg_data()

        self._debug_overlay = DebugOverlay(
            font=self.font,
            engine=self._engine,
            tile_size=TILE_SIZE,
        )

    @override
    def process(self, dt: float):
        width, height = self.screen.get_size()
        player = PlayerView.get()
        player_pos = player.pos

        offset_x, offset_y = self._camera.update(player_pos, dt, width, height)

        draw_tiled_background(self.screen, self._background, offset_x, offset_y)

        aura = player.aura()
        if aura is not None and aura.active:
            r = int(aura.radius)
            aura_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(aura_surf, (120, 220, 120, 45), (r, r), r)
            pygame.draw.circle(aura_surf, (150, 240, 150, 110), (r, r), r, 2)
            self.screen.blit(
                aura_surf,
                (player_pos.x + offset_x - r, player_pos.y + offset_y - r),
            )

        for _, (pos, sprite) in esper.get_components(Position, Sprite):
            self.screen.blit(
                sprite.surface,
                (
                    pos.x + offset_x - sprite.surface.get_width() / 2,
                    pos.y + offset_y - sprite.surface.get_height() / 2,
                ),
            )

        if self._engine.debug_enabled:
            for _, (_, pos, hitbox) in esper.get_components(
                CampfireTag, Position, Hitbox
            ):
                hx = int(pos.x + hitbox.offset_x + offset_x - hitbox.width / 2)
                hy = int(pos.y + hitbox.offset_y + offset_y - hitbox.height / 2)
                hitbox_surf = pygame.Surface(
                    (int(hitbox.width), int(hitbox.height)), pygame.SRCALPHA
                )
                hitbox_surf.fill((0, 255, 0, 120))
                self.screen.blit(hitbox_surf, (hx, hy))
                # exclusion zone autour du feu
                pygame.draw.circle(
                    self.screen,
                    (255, 80, 0),
                    (int(pos.x + offset_x), int(pos.y + offset_y)),
                    700,
                    2,
                )

            px = int(player_pos.x + offset_x)
            py = int(player_pos.y + offset_y)
            pygame.draw.circle(self.screen, (0, 180, 255), (px, py), 300, 2)
            pygame.draw.circle(self.screen, (0, 80, 255), (px, py), 800, 2)

            hx = int(
                player.pos.x
                + player.hitbox.offset_x
                + offset_x
                - player.hitbox.width / 2
            )
            hy = int(
                player.pos.y
                + player.hitbox.offset_y
                + offset_y
                - player.hitbox.height / 2
            )
            surf = pygame.Surface(
                (int(player.hitbox.width), int(player.hitbox.height)),
                pygame.SRCALPHA,
            )
            surf.fill((0, 100, 255, 120))
            self.screen.blit(surf, (hx, hy))

            for _, (_, epos, ehit) in esper.get_components(EnemyTag, Position, Hitbox):
                hx = int(epos.x + ehit.offset_x + offset_x - ehit.width / 2)
                hy = int(epos.y + ehit.offset_y + offset_y - ehit.height / 2)
                surf = pygame.Surface(
                    (int(ehit.width), int(ehit.height)), pygame.SRCALPHA
                )
                surf.fill((255, 0, 0, 120))
                self.screen.blit(surf, (hx, hy))

        fps = int(1.0 / dt) if dt > 0 else 0
        num_ent = sum(1 for _ in esper.get_entities())
        fps_text = self.font.render(
            f"FPS: {max(0, min(fps, 999))} ",
            True,
            pygame.Color("black"),
        )
        self.screen.blit(fps_text, (width - fps_text.get_width() - 10, 10))

        campfires = esper.get_components(CampfireTag, Health)
        if campfires:
            _, (_, c_health) = campfires[0]
            bar_w = 300
            bar_h = 20
            bar_x = (width - bar_w) // 2
            bar_y = 10
            ratio = max(0.0, c_health.current / c_health.max)
            pygame.draw.rect(self.screen, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(
                self.screen, (0, 200, 0), (bar_x, bar_y, int(bar_w * ratio), bar_h)
            )
            label = self.font.render(
                f"Feu de camp : {int(c_health.current)}/{int(c_health.max)}",
                True,
                pygame.Color("white"),
            )
            self.screen.blit(
                label,
                (
                    bar_x + (bar_w - label.get_width()) // 2,
                    bar_y + (bar_h - label.get_height()) // 2,
                ),
            )

        # barre de pv du joueur
        bar_w = 200
        bar_h = 20
        bar_x = 10
        bar_y = 10
        ratio = max(0.0, player.hp.current / player.hp.max)
        pygame.draw.rect(self.screen, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
        pygame.draw.rect(
            self.screen, (0, 200, 0), (bar_x, bar_y, int(bar_w * ratio), bar_h)
        )
        label = self.font.render(
            f"PV : {int(player.hp.current)}/{int(player.hp.max)}",
            True,
            pygame.Color("white"),
        )
        self.screen.blit(
            label,
            (
                bar_x + (bar_w - label.get_width()) // 2,
                bar_y + (bar_h - label.get_height()) // 2,
            ),
        )
        # si le joueur subit un dégat : flash rouge
        if player.invincibility.time > 0:
            alpha = int((player.invincibility.time / INVINCIBILITY_AFTER_HIT) * 80)
            flash = pygame.Surface((width, height), pygame.SRCALPHA)
            flash.fill((255, 0, 0, alpha))
            self.screen.blit(flash, (0, 0))

        self._debug_overlay.draw(
            self.screen,
            dt,
            fps,
            num_ent,
            width,
            offset_x,
            offset_y,
            self._camera.x,
            self._camera.y,
        )

        gold = player.inv.count(ItemKind.GOLD)
        icon = self._item_icons.get(ItemKind.GOLD)
        y = 10 + self.font.get_linesize() + 6
        if icon is not None:
            self.screen.blit(icon, (10, y))
            gold_text = self.font.render(f"{gold}", True, pygame.Color("black"))
            self.screen.blit(
                gold_text,
                (
                    10 + icon.get_width() + 4,
                    y + (icon.get_height() - gold_text.get_height()) // 2,
                ),
            )
        else:
            gold_text = self.font.render(f"Gold: {gold}", True, pygame.Color("black"))
            self.screen.blit(gold_text, (10, y))

        y = y + self.font.get_linesize() + 6
        self._draw_dash_bar(player, y)
        self._draw_weapon_hud(player, y + 18)
        self._draw_status_hud(player, y + 36)

    def _draw_status_hud(self, player: PlayerView, y: int) -> None:
        parts: list[str] = []
        perks = player.perks()
        if perks is not None:
            if perks.crit_chance > 0:
                parts.append(f"Crit {int(perks.crit_chance * 100)}%")
            if perks.lifesteal > 0:
                parts.append(f"Vol {int(perks.lifesteal * 100)}%")
            if perks.pierce:
                parts.append("Perforation")
        objects = player.objects()
        if objects is not None:
            parts.extend(_OBJECT_NAMES[k] for k in objects.owned if k in _OBJECT_NAMES)
        if not parts:
            return
        label = self.font.render("  ·  ".join(parts), True, pygame.Color(20, 20, 20))
        self.screen.blit(label, (10, y))

    def _draw_weapon_hud(self, player: PlayerView, y: int) -> None:
        arsenal = player.arsenal()
        if arsenal is None:
            return

        x = 10
        for i, kind in enumerate(WEAPON_ORDER):
            owned = kind in arsenal.owned
            active = arsenal.active == kind
            if active:
                color = pygame.Color(0, 220, 255)
            elif owned:
                color = pygame.Color(20, 20, 20)
            else:
                color = pygame.Color(120, 120, 120)
            label = self.font.render(f"{i + 1}:{WEAPON_INFO[kind].name}", True, color)
            self.screen.blit(label, (x, y))
            x += label.get_width() + 12

    def _draw_dash_bar(self, player: PlayerView, y: int) -> None:
        try:
            dash = esper.component_for_entity(player.ent, Dash)
        except KeyError:
            return

        bar_w = 120
        bar_h = 10
        bar_x = 10
        ready = dash.cooldown_time <= 0
        ratio = 1.0 if ready else 1.0 - dash.cooldown_time / dash.cooldown
        ratio = max(0.0, min(1.0, ratio))

        pygame.draw.rect(self.screen, (40, 40, 40), (bar_x, y, bar_w, bar_h))
        fill_color = (0, 220, 255) if ready else (0, 110, 140)
        pygame.draw.rect(self.screen, fill_color, (bar_x, y, int(bar_w * ratio), bar_h))
        label = self.font.render("Dash [Maj]", True, pygame.Color("black"))
        self.screen.blit(
            label, (bar_x + bar_w + 8, y - (label.get_height() - bar_h) // 2)
        )
