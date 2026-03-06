import pygame
import esper
from client.component.physics import Position, Velocity
from client.factory.player import create_player


class InputSystem:
    def process(self):
        keys = pygame.key.get_pressed()
        for ent, (vel) in esper.get_component(Velocity):
            vel.vx = 0
            vel.vy = 0
            if keys[pygame.K_z]:
                vel.vy -= 10
            if keys[pygame.K_s]:
                vel.vy += 10
            if keys[pygame.K_q]:
                vel.vx -= 10
            if keys[pygame.K_d]:
                vel.vx += 10


class MovementSystem:
    def process(self):
        for ent, (vel, pos) in esper.get_components(Velocity, Position):
            pos.x += vel.vx
            pos.y += vel.vy


# pygame setup
def main():
    pygame.init()
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h))
    clock = pygame.time.Clock()
    running = True

    esper.add_processor(InputSystem())
    esper.add_processor(MovementSystem())

    create_player(Position(info.current_w / 2, info.current_h / 2))

    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        esper.process()
        # fill the screen with a color to wipe away anything from last frame
        screen.fill("purple")
        for ent, (pos) in esper.get_component(Position):
            pygame.draw.circle(screen, "black", (pos.x, pos.y), radius=40)
        # RENDER YOUR GAME HERE

        # flip() the display to put your work on screen
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

    pygame.quit()
