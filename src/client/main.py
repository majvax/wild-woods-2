import math
from typing import cast, final, override

import esper
import pygame
from esper import Processor

from client.component import PlayerTag, Position, Speed, Sprite, Velocity
from client.core import Engine, Scene, generate_background_surface
from client.factory import create_bandit, create_player
from client.processor import BrainProc, LootSystem, TargetingProc
from client.ui import NEON_PURPLE, NEON_PURPLE_SWITCH, Button, ToggleSwitch


@final
class InputSystem(Processor):
    @override
    def process(self, _):
        keys = pygame.key.get_pressed()
        for _, (vel, speed, _) in esper.get_components(Velocity, Speed, PlayerTag):
            vel.vx = 0
            vel.vy = 0
            if keys[pygame.K_z]:
                vel.vy -= speed.value
            if keys[pygame.K_s]:
                vel.vy += speed.value
            if keys[pygame.K_q]:
                vel.vx -= speed.value
            if keys[pygame.K_d]:
                vel.vx += speed.value

            if vel.vx != 0 and vel.vy != 0:
                vel.vx /= math.sqrt(2)
                vel.vy /= math.sqrt(2)


@final
class MovementSystem(Processor):
    @override
    def process(self, dt: float):
        for _, (vel, pos) in esper.get_components(Velocity, Position):
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt


@final
class RenderSystem(Processor):
    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 18)
        largeur, hauteur = self.screen.get_size()
        self._background = generate_background_surface(largeur, hauteur)

    @override
    def process(self, dt: float):
        self.screen.fill("white")
        self.screen.blit(self._background)
        for _, (pos, sprite) in esper.get_components(Position, Sprite):
            self.screen.blit(
                sprite.surface,
                (
                    pos.x - sprite.surface.get_width() / 2,
                    pos.y - sprite.surface.get_height() / 2,
                ),
            )
        fps = int(1.0 / dt) if dt > 0 else 0
        num_ent = len(list(esper.get_entities()))
        fps_text = self.font.render(
            f"FPS: {max(0, min(fps, 999))} | {num_ent} ENTITIES",
            True,
            pygame.Color("black"),
        )
        self.screen.blit(fps_text, (10, 10))


@final
class PauseScene(Scene):
    _screen: pygame.Surface

    def __init__(self, engine: Engine):
        super().__init__()
        self._screen = engine.screen
        self._engine = engine

        w, h = self._screen.get_size()
        self._btn_resume = Button(
            "Reprendre", NEON_PURPLE, 28, 12, 10, 18, on_click=self._resume
        )
        self._btn_quit = Button(
            "Quitter", NEON_PURPLE, 28, 12, 10, 18, on_click=self._quit
        )
        self._font_label = pygame.font.SysFont("Arial", 18)
        # Calcul de la position pour centrer "Son" + switch horizontalement
        label_w, _ = self._font_label.size("Son")
        gap, switch_w, switch_h = 10, 60, 28
        total_w = label_w + gap + switch_w
        self._sound_label_x = w // 2 - total_w // 2  # bord gauche du label
        self._sound_switch = ToggleSwitch(NEON_PURPLE_SWITCH, switch_w, switch_h)
        switch_cx = (
            w // 2 - total_w // 2 + label_w + gap + switch_w // 2
        )  # centre du switch
        switch_y = h // 2 + 110 - switch_h // 2

        self._btn_resume.set_rect(w // 2, h // 2 - 30)
        self._btn_quit.set_rect(w // 2, h // 2 + 35)
        self._sound_switch.set_rect(switch_cx, switch_y)

    def _resume(self) -> None:
        self._engine.sm.pop()

    def _quit(self) -> None:
        self._engine.stop()

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if cast(int, event.key) in (pygame.K_ESCAPE, pygame.K_p):
                    self._resume()

        for btn in (self._btn_resume, self._btn_quit):
            btn.update(dt, events)
            btn.draw(self._screen)

        label = self._font_label.render("Son", True, pygame.Color(200, 184, 255))
        self._screen.blit(
            label,
            (
                self._sound_label_x,
                self._sound_switch.rect.centery - label.get_height() // 2,
            ),
        )
        self._sound_switch.update(dt, events)
        self._sound_switch.draw(self._screen)

        return False


@final
class GameScene(Scene):
    _screen: pygame.Surface
    _timer: float

    def __init__(self, engine: Engine):
        super().__init__()
        self._screen = engine.screen
        self._timer = 0.0
        self._engine = engine

    @override
    def on_enter(self) -> None:
        esper.add_processor(InputSystem())
        esper.add_processor(TargetingProc())
        esper.add_processor(BrainProc())
        esper.add_processor(LootSystem())
        esper.add_processor(MovementSystem())
        esper.add_processor(RenderSystem(self._screen))

        create_player(Position(self._screen.size[0] / 2, self._screen.size[1] / 2))
        create_bandit(Position(400, 400))

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if cast(int, event.key) in (pygame.K_ESCAPE, pygame.K_p):
                    self._engine.sm.push(PauseScene, self._engine)
                    return True

        # Spawn bandits every 5 seconds
        # self._timer += dt
        # if self._timer > 0.1:
        #     pos = Position(
        #         self._screen.get_width() * 0.1
        #         + self._screen.get_width() * 0.8 * random.random(),
        #         self._screen.get_height() * 0.1
        #         + self._screen.get_height() * 0.8 * random.random(),
        #     )
        #     create_bandit(pos)
        #     self._timer = 0

        esper.process(dt)

        return True


def main() -> int:
    engine = Engine()
    engine.sm.push(GameScene, engine)
    return engine.run()


if __name__ == "__main__":
    raise SystemExit(main())
