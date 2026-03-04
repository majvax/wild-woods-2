from unittest.mock import MagicMock, call, patch

import pytest

from client.core.scene import Scene


class DummyScene(Scene):
    """Minimal Scene that records lifecycle calls."""

    def __init__(self, *, propagate: bool = False) -> None:
        self.entered = False
        self.exited = False
        self.process_calls: list[float] = []
        self._propagate = propagate
        super().__init__()

    def on_enter(self) -> None:
        self.entered = True

    def process(self, dt: float) -> bool:
        self.process_calls.append(dt)
        return self._propagate

    def on_exit(self) -> None:
        self.exited = True


class MinimalScene(Scene):
    """Scene that implements only the required methods."""

    def on_enter(self) -> None:
        pass

    def process(self, dt: float) -> bool:
        return False


def test_on_enter_called_on_init():
    scene = DummyScene()
    assert scene.entered is True


def test_world_id_unique():
    a = DummyScene()
    b = DummyScene()
    assert a._id != b._id


@patch("client.core.scene.esper")
def test_init_switches_world(mock: MagicMock):
    scene = DummyScene()
    mock.switch_world.assert_called_with(scene._id)


@patch("client.core.scene.esper")
def test_process_switches_world_and_delegates(mock: MagicMock):
    scene = DummyScene()
    mock.reset_mock()

    result = scene._process(0.016)

    mock.switch_world.assert_called_once_with(scene._id)
    assert result is False
    assert scene.process_calls == [0.016]


@patch("client.core.scene.esper")
def test_cleanup_switches_world_calls_on_exit_and_deletes(mock: MagicMock):
    scene = DummyScene()
    mock.reset_mock()
    scene._cleanup()
    assert scene.exited is True
    assert mock.switch_world.call_count == 2
    mock.switch_world.assert_any_call(scene._id)
    mock.switch_world.assert_any_call("default")
    mock.delete_world.assert_called_once_with(scene._id)


def test_on_exit_default_is_noop():
    scene = MinimalScene()
    scene.on_exit()


def test_scene_is_abstract():
    with pytest.raises(TypeError):
        Scene()  # type: ignore[abstract]


@patch("client.core.scene.esper")
def test_cleanup_calls_in_correct_order(mock: MagicMock):
    """on_exit() must run while the scene world is active, before deletion."""
    scene = DummyScene()
    mock.reset_mock()
    scene._cleanup()

    expected_calls = [
        call.switch_world(scene._id),
        call.switch_world("default"),
        call.delete_world(scene._id),
    ]
    assert mock.method_calls == expected_calls


def test_process_returns_true_when_propagate():
    scene = DummyScene(propagate=True)
    assert scene._process(0.016) is True
