from enum import IntEnum, auto
from typing import final

import esper
import pygame

from client.scene import SceneManager

from .event import EngineEvent


class StopCode(IntEnum):
    NORMAL = 0
    ERROR = auto()


@final
class Engine:
    _is_running: bool = True
    _is_initialized: bool = False
    _stop_code: StopCode = StopCode.NORMAL
    _scene_manger: SceneManager = SceneManager()
    _clock: pygame.time.Clock = pygame.time.Clock()
    _screen: pygame.Surface
    _snow_enabled: bool = False
    _snow_paused: bool = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def sm(self) -> SceneManager:
        return self._scene_manger

    @property
    def screen(self) -> pygame.Surface:
        return self._screen

    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF
        )
        esper.set_handler(EngineEvent.STOP, self.stop)

    def stop(self, *, code: StopCode = StopCode.NORMAL):
        self._is_running = False
        self._stop_code = code

    @property
    def snow_enabled(self) -> bool:
        return self._snow_enabled

    @property
    def snow_paused(self) -> bool:
        return self._snow_paused

    def set_snow_enabled(self, enabled: bool) -> None:
        self._snow_enabled = enabled

    def set_snow_paused(self, paused: bool) -> None:
        self._snow_paused = paused

    def run(self) -> StopCode:
        while self.is_running:
            dt = self._clock.tick() / 1000

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.stop()

            self._scene_manger.process(dt, events)
            pygame.display.flip()

        return self._stop_code
