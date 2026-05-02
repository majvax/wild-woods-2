from typing import override
from unittest.mock import MagicMock, patch

import pygame

from client.scene import Scene


class DummyScene(Scene):
    """Minimal Scene that records lifecycle calls."""

    def __init__(self, *, propagate: bool = False) -> None:
        self.entered: bool = False
        self.exited: bool = False
        self.process_calls: list[float] = []
        self._propagate: bool = propagate
        super().__init__()

    @override
    def on_enter(self) -> None:
        self.entered = True

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        self.process_calls.append(dt)
        return self._propagate

    @override
    def on_exit(self) -> None:
        self.exited = True


class MinimalScene(Scene):
    """Scene that implements only the required methods."""

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        return False


def test_on_enter_called_on_init():
    scene = DummyScene()
    assert scene.entered is False


def test_world_id_unique():
    a = DummyScene()
    b = DummyScene()
    assert a.id != b.id


@patch("client.scene.scene.esper")
def test_process_switches_world_and_delegates(mock: MagicMock):
    scene = DummyScene()
    mock.reset_mock()

    events = pygame.event.get()
    result = scene.process(0.016, events)

    assert result is False
    assert scene.process_calls == [0.016]


def test_on_exit_default_is_noop():
    scene = MinimalScene()
    scene.on_exit()


def test_process_returns_true_when_propagate():
    scene = DummyScene(propagate=True)
    events = pygame.event.get()
    assert scene.process(0.016, events) is True
