# tests/conftest.py
from unittest.mock import patch
import pytest


@pytest.fixture(autouse=True)
def mock_pygame_events():
    with patch("pygame.event.get", return_value=[]):
        yield