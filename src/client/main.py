from client.core import Difficulty, Engine
from client.scene.main_menu import MainMenuScene


def main() -> int:
    engine = Engine()

    def go_to_menu() -> None:
        engine.sm.clear()
        engine.sm.push(MainMenuScene, engine, start_game)

    def start_game(difficulty: Difficulty) -> None:
        from client.scene.game import GameScene

        engine.sm.pop()
        engine.sm.push(GameScene, engine, difficulty, go_to_menu)

    engine.sm.push(MainMenuScene, engine, start_game)
    return engine.run()


if __name__ == "__main__":
    raise SystemExit(main())
