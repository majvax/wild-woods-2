from typing import cast, final, override

import esper
import pygame

from client.component import Position
from client.core import Engine, Scene
from client.factory import create_bandit, create_player
from client.processor import (
    BrainProc,
    InputProc,
    LootProc,
    MovementProc,
    RenderProc,
    TargetingProc,
)
from client.ui import NEON_PURPLE, NEON_PURPLE_SWITCH, Button, ToggleSwitch


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
        esper.add_processor(InputProc())
        esper.add_processor(TargetingProc())
        esper.add_processor(BrainProc())
        esper.add_processor(LootProc())
        esper.add_processor(MovementProc())
        esper.add_processor(RenderProc(self._screen))

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
