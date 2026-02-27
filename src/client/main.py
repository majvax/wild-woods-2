import sys

import pygame


def main() -> None:
    pygame.init()

    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.SCALED)
    pygame.display.set_caption("Wild Woods 2")

    clock = pygame.time.Clock()
    running = True

    pos: list[float] = [screen_width / 2, screen_height / 2]
    speed: float = 400.0

    while running:
        dt: float = clock.tick(120) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_s]:
            pos[1] += speed * dt
        if keys[pygame.K_z]:
            pos[1] -= speed * dt
        if keys[pygame.K_q]:
            pos[0] -= speed * dt
        if keys[pygame.K_d]:
            pos[0] += speed * dt

        screen.fill((30, 30, 40))

        pygame.draw.rect(
            screen,
            (0, 255, 100),
            (pos[0] - 25, pos[1] - 25, 50, 50),
        )

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
