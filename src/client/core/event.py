from enum import StrEnum, unique
from uuid import uuid4


@unique
class EngineEvent(StrEnum):
    """Enum for the different types of events that can occur in the game."""

    STOP = uuid4().hex
