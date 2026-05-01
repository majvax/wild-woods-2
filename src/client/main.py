from client.core import Engine
from client.scene.game import GameScene


def main() -> int:
    engine = Engine()
    engine.sm.push(GameScene, engine)
    return engine.run()


if __name__ == "__main__":
    raise SystemExit(main())
