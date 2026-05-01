import esper
import pygame

from client.core import Engine, EngineEvent, SceneManager, StopCode


def test_engine_stop_sets_code(monkeypatch):
    monkeypatch.setattr(pygame, "init", lambda: None)
    monkeypatch.setattr(pygame.display, "set_mode", lambda *_: pygame.Surface((10, 10)))
    monkeypatch.setattr(esper, "set_handler", lambda *_: None)

    Engine._scene_manger = SceneManager()
    engine = Engine()

    engine.stop(code=StopCode.ERROR)

    assert engine.is_running is False
    assert engine.run() == StopCode.ERROR


def test_engine_run_handles_quit(monkeypatch):
    monkeypatch.setattr(pygame, "init", lambda: None)
    monkeypatch.setattr(pygame.display, "set_mode", lambda *_: pygame.Surface((10, 10)))
    monkeypatch.setattr(pygame.display, "flip", lambda: None)

    called = {}

    def fake_set_handler(event, handler):
        called["event"] = event
        called["handler"] = handler

    monkeypatch.setattr(esper, "set_handler", fake_set_handler)

    quit_event = pygame.event.Event(pygame.QUIT)
    monkeypatch.setattr(pygame.event, "get", lambda: [quit_event])

    Engine._scene_manger = SceneManager()
    engine = Engine()

    assert called["event"] == EngineEvent.STOP
    assert called["handler"] == engine.stop

    assert engine.run() == StopCode.NORMAL
