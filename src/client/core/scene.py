import uuid
from abc import ABC, abstractmethod

import esper


class Scene(ABC):
    def __init__(self) -> None:
        self._id = uuid.uuid4().hex
        esper.switch_world(self._id)
        self.on_enter()

    def _process(self, dt: float) -> bool:
        esper.switch_world(self._id)
        return self.process(dt)

    def _cleanup(self) -> None:
        esper.switch_world(self._id)
        self.on_exit()
        esper.switch_world("default")
        esper.delete_world(self._id)

    @abstractmethod
    def on_enter(self) -> None: ...

    @abstractmethod
    def process(self, dt: float) -> bool:
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

    def push[T: Scene](self, scene: type[T], *args, **kwargs) -> T:
        """Push a new scene on top of the stack.

        Args:
            scene: The scene class to instantiate and push.
            *args, **kwargs: Arguments to pass to the scene constructor.

        Returns:
            The instance of the scene that was created and pushed.
        """
        instance = scene(*args, **kwargs)
        self._scenes.append(instance)
        return instance

    def pop(self) -> None:
        if not self._scenes:
            return
        self._scenes[-1]._cleanup()
        self._scenes.pop()

    def process(self, dt: float) -> None:
        for scene in reversed(self._scenes):
            if not scene._process(dt):
                break
