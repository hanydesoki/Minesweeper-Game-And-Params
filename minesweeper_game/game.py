import pygame

from .layout import Layout
from .settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS


# print(__name__)

def run_game() -> None:

    pygame.init()

    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Minesweeper")


    # menu_thread = threading.Thread(target=parameter_menu.update)
    # menu_thread.start()

    layout: Layout = Layout(grid_size=(10, 15), number_mines=25)

    clock: pygame.time.Clock = pygame.time.Clock()

    run_loop: bool = True


    while run_loop:

        all_events: list[pygame.event.Event] = pygame.event.get()

        for event in all_events:
            if event.type == pygame.QUIT:
                run_loop = False

        # print(all_events)
        layout.update(all_events)

        clock.tick(FPS)

        pygame.display.update()

   