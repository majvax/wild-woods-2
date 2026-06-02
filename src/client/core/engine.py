from enum import IntEnum, auto
from typing import cast, final

import esper
import pygame

from client.scene import SceneManager

from .event import EngineEvent


class StopCode(IntEnum):
    NORMAL = 0
    ERROR = auto()


@final
class Engine:
    def __init__(self):
        pygame.init()
        self._screen = pygame.display.set_mode(
            (0, 0), pygame.FULLSCREEN | pygame.DOUBLEBUF
        )
        esper.set_handler(EngineEvent.STOP, self.stop)
        self._scene_manager = SceneManager()
        self._clock = pygame.time.Clock()
        self._is_running: bool = True
        self._stop_code: StopCode = StopCode.NORMAL
        self._debug_enabled: bool = False
        self._debug_paused: bool = False
        self._debug_step_requested: bool = False
        self._debug_step_dt: float = 1 / 60

    @property
    def is_running(self) -> bool:
        return self._is_running

    @property
    def sm(self) -> SceneManager:
        return self._scene_manager

    @property
    def screen(self) -> pygame.Surface:
        return self._screen

    @property
    def debug_enabled(self) -> bool:
        return self._debug_enabled

    @property
    def debug_paused(self) -> bool:
        return self._debug_paused

    @property
    def debug_step_dt(self) -> float:
        return self._debug_step_dt

    def stop(self, *, code: StopCode = StopCode.NORMAL):
        self._is_running = False
        self._stop_code = code

    def _handle_engine_keys(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.QUIT:
                self.stop()
                continue
            if event.type != pygame.KEYDOWN:
                continue

            key = cast(int, event.key)
            if key == pygame.K_RSHIFT:
                self._debug_enabled = not self._debug_enabled
                if not self._debug_enabled:
                    self._debug_paused = False
                self._debug_step_requested = False
            elif key == pygame.K_RCTRL and self._debug_enabled:
                self._debug_paused = not self._debug_paused
                self._debug_step_requested = False
            elif key == pygame.K_RIGHT and self._debug_enabled and self._debug_paused:
                self._debug_step_requested = True

    def _resolve_dt(self, dt: float) -> float:
        if not (self._debug_enabled and self._debug_paused):
            return dt
        if self._debug_step_requested:
            self._debug_step_requested = False
            return self._debug_step_dt
        return 0.0

    def run(self) -> StopCode:
        while self._is_running:
            dt = self._clock.tick() / 1000
            events = pygame.event.get()
            self._handle_engine_keys(events)
            dt = self._resolve_dt(dt)
            self._scene_manager.process(dt, events)
            pygame.display.flip()
        return self._stop_code
