import pygame
import pytest

from client.ui.components import (
    NEON_PURPLE,
    NEON_PURPLE_SWITCH,
    Button,
    ToggleSwitch,
)
from client.ui.helper import lerp_color


@pytest.fixture(scope="module", autouse=True)
def init_pygame_font():
    pygame.font.init()
    yield
    pygame.font.quit()


def test_lerp_color_clamps_bounds():
    a = pygame.Color(0, 0, 0)
    b = pygame.Color(255, 255, 255)

    assert lerp_color(a, b, -1.0) == a
    assert lerp_color(a, b, 2.0) == b


def test_button_click_invokes_handler(monkeypatch):
    clicked = {"value": False}

    def on_click() -> None:
        clicked["value"] = True

    button = Button("OK", NEON_PURPLE, 10, 5, 4, on_click=on_click)
    button.set_rect(50, 20)

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: button.rect.center)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
    button.update(0.016, [event])

    assert clicked["value"] is True


def test_button_disabled_skips_interaction(monkeypatch):
    button = Button("OK", NEON_PURPLE, 10, 5, 4, enabled=False)
    button.set_rect(50, 20)

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: button.rect.center)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
    button.update(0.016, [event])

    surface = pygame.Surface((100, 60))
    button.draw(surface)

    assert button.enabled is False


def test_toggle_switch_toggles_on_click(monkeypatch):
    values: list[bool] = []

    def on_toggle(value: bool) -> None:
        values.append(value)

    switch = ToggleSwitch(NEON_PURPLE_SWITCH, 60, 28, value=False, on_toggle=on_toggle)
    switch.set_rect(50, 20)

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: switch.rect.center)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
    switch.update(0.016, [event])

    assert switch.value is True
    assert values == [True]


def test_toggle_switch_disabled_draws(monkeypatch):
    switch = ToggleSwitch(NEON_PURPLE_SWITCH, 60, 28, value=False, enabled=False)
    switch.set_rect(50, 20)

    monkeypatch.setattr(pygame.mouse, "get_pos", lambda: switch.rect.center)
    event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
    switch.update(0.016, [event])

    surface = pygame.Surface((100, 60))
    switch.draw(surface)

    assert switch.enabled is False
