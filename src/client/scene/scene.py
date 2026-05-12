import uuid
from abc import ABC, abstractmethod
from typing import final

import esper
import pygame


class Scene(ABC):
    def __init__(self) -> None:
        self._id: str = uuid.uuid4().hex

    @final
    @property
    def id(self) -> str:
        return self._id

    @abstractmethod
    def on_enter(self) -> None: ...

    @abstractmethod
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        """Called every frame.

        Returns:
            True  — allow scenes below to process.
            False — stop propagation to scenes below.
        """
        ...

    def on_exit(self) -> None: ...


class SceneManager:
    def __init__(self) -> None:
        self._scenes: list[Scene] = []

    @property
    def current(self) -> Scene | None:
        """Get the current active scene (the one on top of the stack)."""
        return self._scenes[-1] if self._scenes else None

    @property
    def empty(self) -> bool:
        """Check if there are no scenes in the stack."""
        return not self._scenes

    def push[T: Scene](self, scene: type[T], *args: object, **kwargs: object) -> T:
        """Push a new scene on top of the stack.

        Args:
            scene: The scene class to instantiate and push.
            *args, **kwargs: Arguments to pass to the scene constructor.

        Returns:
            The instance of the scene that was created and pushed.
        """
        instance = scene(*args, **kwargs)
        esper.switch_world(instance.id)
        instance.on_enter()
        self._scenes.append(instance)
        return instance

    def pop(self) -> None:
        if not self._scenes:
            return
        scene = self._scenes[-1]
        esper.switch_world(scene.id)
        scene.on_exit()
        esper.switch_world("default")
        esper.delete_world(scene.id)
        self._scenes.pop()

    def process(self, dt: float, events: list[pygame.event.Event]) -> None:
        for scene in reversed(self._scenes):
            esper.switch_world(scene.id)
            if not scene.process(dt, events):
                break

    def clear(self) -> None:
        while not self.empty:
            self.pop()
