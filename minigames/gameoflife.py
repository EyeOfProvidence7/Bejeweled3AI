import pygame
import pygame_gui
import numpy as np
from scipy.signal import convolve2d
import colorsys
import math

# Config
CELL_SIZE = 10
GRID_WIDTH = 160
GRID_HEIGHT = 120
UI_WIDTH_PIXELS = 400
INITIAL_FPS = 10

# Colors
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

RULE_STRING = "B3/S23"

def parse_rule(rule_str):
    birth = []
    survive = []
    rule_str = rule_str.strip().upper()
    if "B" in rule_str and "S" in rule_str:
        b_section = rule_str.split("S")[0].replace("B", "").replace("/", "")
        s_section = rule_str.split("S")[1].replace("/", "")
        birth = [int(n) for n in b_section if n.isdigit()]
        survive = [int(n) for n in s_section if n.isdigit()]
    return birth, survive

def update_grid(grid, birth_rules, survive_rules):
    kernel = np.array([[1, 1, 1],
                       [1, 0, 1],
                       [1, 1, 1]])
    neighbors = convolve2d(grid, kernel, mode='same', boundary='wrap')
    birth = np.isin(neighbors, birth_rules) & (grid == 0)
    survive = np.isin(neighbors, survive_rules) & (grid == 1)
    return (birth | survive).astype(np.uint8)

def draw_grid(screen, grid, psychedelic_mode):
    if not psychedelic_mode:
        # Standard white cells on black
        screen.fill(BLACK, pygame.Rect(0, 0, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y, x] == 1:
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
                    pygame.draw.rect(screen, YELLOW, rect)
        return  # Skip the psychedelic stuff

    t = pygame.time.get_ticks() / 1000.0

    # Optional: animated dark background
    bg_hue = (t * 0.05) % 1.0
    bg_rgb = colorsys.hsv_to_rgb(bg_hue, 0.2, 0.07)
    bg_color = tuple(int(c * 255) for c in bg_rgb)
    screen.fill(bg_color, pygame.Rect(0, 0, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))

    angle = t * 0.2
    dx = math.cos(angle)
    dy = math.sin(angle)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y, x] == 1:
                weirdness = math.sin(abs(x * 0.05 + t) ** 1.2) * math.cos(abs(y * 0.05 - t) ** 1.1)
                warp = math.sin(x * 0.1 + y * 0.1 + t * 3) * 0.5

                hue = (0.5 + 0.5 * math.sin(((x * dx + y * dy) * 0.02 + t * 0.5 + weirdness + warp))) % 1.0

                rgb = colorsys.hsv_to_rgb(hue, 1, 1)
                color = tuple(int(c * 255) for c in rgb)
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
                pygame.draw.rect(screen, color, rect)

def main():
    pygame.init()
    screen_size = (GRID_WIDTH * CELL_SIZE + UI_WIDTH_PIXELS, GRID_HEIGHT * CELL_SIZE)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Conway's Game of Life with pygame_gui")
    clock = pygame.time.Clock()
    psychedelic_mode = False

    # GUI manager
    manager = pygame_gui.UIManager(screen_size)

    label_x = GRID_WIDTH * CELL_SIZE + 20
    element_x = label_x + 180  # Controls now to the right

    # FPS Slider
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((label_x, 20), (160, 24)),
        text="FPS",
        manager=manager
    )
    slider = pygame_gui.elements.UIHorizontalSlider(
        relative_rect=pygame.Rect((element_x, 20), (160, 24)),
        start_value=INITIAL_FPS,
        value_range=(1, 60),
        manager=manager
    )

    # Pause button
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((label_x, 60), (160, 30)),
        text="Pause simulation",
        manager=manager
    )
    pause_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((element_x, 60), (75, 30)),
        text='Pause',
        manager=manager
    )

    # Step button
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((label_x, 95), (160, 30)),
        text="Step once",
        manager=manager
    )
    step_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((element_x, 95), (75, 30)),
        text='Step',
        manager=manager
    )

    # Rule input
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((label_x, 140), (160, 30)),
        text="Rule (e.g. B3/S23)",
        manager=manager
    )
    rule_input = pygame_gui.elements.UITextEntryLine(
        relative_rect=pygame.Rect((element_x, 140), (160, 30)),
        manager=manager
    )
    rule_input.set_text(RULE_STRING)

    # Randomize button
    randomize_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((element_x, 180), (160, 30)),
        text='Randomize',
        manager=manager
    )
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((label_x, 180), (160, 30)),
        text="Randomize grid",
        manager=manager
    )

    # Psychedelic Mode toggle
    pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((label_x, 220), (160, 30)),
        text="Psychedelic mode",
        manager=manager
    )
    psy_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((element_x, 220), (160, 30)),
        text="Turn On",
        manager=manager
    )


    grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])
    birth_rules, survive_rules = parse_rule(RULE_STRING)

    fps = INITIAL_FPS
    sim_interval = 1000 / fps
    time_since_last_step = 0
    paused = False
    step_requested = False

    running = True
    while running:
        time_delta = clock.tick(60)
        time_since_last_step += time_delta

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == pause_button:
                        paused = not paused
                        pause_button.set_text("Play" if paused else "Pause")

                    elif event.ui_element == step_button:
                        step_requested = True

                    elif event.ui_element == randomize_button:
                        grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])

                    elif event.ui_element == psy_button:
                        psychedelic_mode = not psychedelic_mode
                        psy_button.set_text("Turn On" if not psychedelic_mode else "Turn Off")

                elif event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
                    if event.ui_element == rule_input:
                        birth_rules, survive_rules = parse_rule(rule_input.get_text())

            manager.process_events(event)

        manager.update(time_delta / 1000.0)

        if (not paused and time_since_last_step >= sim_interval) or (paused and step_requested):
            grid = update_grid(grid, birth_rules, survive_rules)
            time_since_last_step = 0
            step_requested = False

        fps = int(slider.get_current_value())
        sim_interval = 1000 / fps

        draw_grid(screen, grid, psychedelic_mode)
        manager.draw_ui(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
