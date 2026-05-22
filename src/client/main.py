from client.core import Engine
from client.scene.main_menu import MainMenuScene


def main() -> int:
    engine = Engine()
    engine.sm.push(MainMenuScene, engine)
    return engine.run()


if __name__ == "__main__":
    raise SystemExit(main())
