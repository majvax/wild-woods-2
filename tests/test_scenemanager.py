from typing import final, override

import pygame
import pytest

from client.core import Scene, SceneManager


class DummyScene(Scene):
    """Minimal concrete Scene that records lifecycle calls."""

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


@final
class ArgScene(Scene):
    """Scene that accepts extra constructor arguments."""

    def __init__(self, value: int, *, label: str = "default") -> None:
        self.value = value
        self.label = label
        super().__init__()

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        return False


def test_initial_state():
    sm = SceneManager()
    assert sm.empty is True
    assert sm.current is None


def test_push_returns_instance():
    sm = SceneManager()
    instance = sm.push(DummyScene)
    assert isinstance(instance, DummyScene)


def test_push_sets_current():
    sm = SceneManager()
    scene = sm.push(DummyScene)
    assert sm.current is scene
    assert sm.empty is False


def test_push_forwards_args_and_kwargs():
    sm = SceneManager()
    scene = sm.push(ArgScene, 42, label="hello")
    assert scene.value == 42
    assert scene.label == "hello"


def test_push_stacks_scenes():
    sm = SceneManager()
    sm.push(DummyScene)
    second = sm.push(DummyScene)
    assert sm.current is second


def test_pop_removes_top_scene():
    sm = SceneManager()
    first = sm.push(DummyScene)
    sm.push(DummyScene)
    sm.pop()
    assert sm.current is first


def test_pop_calls_cleanup():
    sm = SceneManager()
    scene = sm.push(DummyScene)
    sm.pop()
    assert scene.exited is True


def test_pop_on_empty_is_noop():
    sm = SceneManager()
    sm.pop()  # should not raise
    assert sm.empty is True


def test_pop_all_makes_empty():
    sm = SceneManager()
    sm.push(DummyScene)
    sm.push(DummyScene)
    sm.pop()
    sm.pop()
    assert sm.empty is True
    assert sm.current is None


def test_process_calls_scenes_in_order():
    sm = SceneManager()
    first = sm.push(DummyScene, propagate=True)
    second = sm.push(DummyScene, propagate=True)

    events = pygame.event.get()
    sm.process(0.016, events)

    assert first.process_calls == [0.016]
    assert second.process_calls == [0.016]


def test_process_stops_propagation_when_false():
    sm = SceneManager()
    first = sm.push(DummyScene, propagate=True)
    second = sm.push(DummyScene, propagate=False)
    third = sm.push(DummyScene, propagate=True)

    events = pygame.event.get()
    sm.process(0.5, events)

    assert third.process_calls == [0.5]
    assert second.process_calls == [0.5]
    assert first.process_calls == []


def test_process_propagates_through_all_when_all_true():
    sm = SceneManager()
    scenes = [sm.push(DummyScene, propagate=True) for _ in range(5)]

    events = pygame.event.get()
    sm.process(1.0, events)

    for s in scenes:
        assert s.process_calls == [1.0]


def test_process_on_empty_manager_is_noop():
    sm = SceneManager()
    events = pygame.event.get()
    sm.process(0.016, events)  # should not raise


def test_push_pop_push_works():
    sm = SceneManager()
    sm.push(DummyScene)
    sm.pop()
    scene = sm.push(DummyScene)
    assert sm.current is scene
    assert sm.empty is False


def test_multiple_process_calls_accumulate():
    sm = SceneManager()
    scene = sm.push(DummyScene)
    events = pygame.event.get()
    sm.process(0.1, events)
    sm.process(0.2, events)
    sm.process(0.3, events)
    assert scene.process_calls == [0.1, 0.2, 0.3]


def test_process_dt_passed_correctly():
    sm = SceneManager()
    scene = sm.push(DummyScene)
    events = pygame.event.get()
    sm.process(0.033, events)
    assert scene.process_calls[-1] == pytest.approx(0.033)


def test_pop_does_not_affect_scenes_below():
    sm = SceneManager()
    first = sm.push(DummyScene)
    sm.push(DummyScene)
    sm.pop()
    assert first.exited is False
    assert first.entered is True


def test_push_triggers_on_enter():
    sm = SceneManager()
    scene = sm.push(DummyScene)
    assert scene.entered is True


def test_process_after_pop():
    sm = SceneManager()
    first = sm.push(DummyScene, propagate=True)
    second = sm.push(DummyScene, propagate=True)
    sm.pop()
    events = pygame.event.get()
    sm.process(0.5, events)
    assert first.process_calls == [0.5]
    assert second.process_calls == []  # was popped, should not receive ticks


def test_single_scene_propagate_false():
    sm = SceneManager()
    scene = sm.push(DummyScene, propagate=False)
    events = pygame.event.get()
    sm.process(0.1, events)
    assert scene.process_calls == [0.1]


def test_push_returns_correct_type():
    sm = SceneManager()
    scene = sm.push(ArgScene, 10)
    assert type(scene) is ArgScene
