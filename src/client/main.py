import math
from typing import final, override

import esper
import pygame
from esper import Processor

from client.component.gameplay import Sprite
from client.component.physics import Position, Speed, Velocity
from client.component.tags import PlayerTag
from client.core.engine import Engine
from client.core.scene import Scene
from client.factory.bandit import create_bandit
from client.factory.player import create_player
from client.processor import BrainProc, TargetingProc


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

    @override
    def process(self, dt: float):
        self.screen.fill("white")
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
class GameScene(Scene):
    _screen: pygame.Surface
    _timer: float

    def __init__(self, engine: Engine):
        super().__init__()
        self._screen = engine.screen
        self._timer = 0.0

    @override
    def on_enter(self) -> None:
        esper.add_processor(InputSystem())
        esper.add_processor(TargetingProc())
        esper.add_processor(BrainProc())
        esper.add_processor(MovementSystem())
        esper.add_processor(RenderSystem(self._screen))

        create_player(Position(self._screen.size[0] / 2, self._screen.size[1] / 2))
        create_bandit(Position(0, 0))

    @override
    def process(self, dt: float) -> bool:
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
