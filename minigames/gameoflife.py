import pygame
import pygame_gui
import numpy as np
from scipy.signal import convolve2d
import colorsys
import math

# Configuration Constants
CELL_SIZE = 10
GRID_WIDTH = 160
GRID_HEIGHT = 120
UI_WIDTH_PIXELS = 400
INITIAL_FPS = 10

# Color Constants
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

# Default Rule
RULE_STRING = "B3/S23"

def parse_rule(rule_str):
    rule_str = rule_str.strip().upper()
    birth = [int(n) for n in rule_str.split("S")[0].replace("B", "").replace("/", "") if n.isdigit()]
    survive = [int(n) for n in rule_str.split("S")[1].replace("/", "") if n.isdigit()]
    return birth, survive

def update_grid(grid, birth_rules, survive_rules):
    kernel = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
    neighbors = convolve2d(grid, kernel, mode='same', boundary='wrap')
    birth = np.isin(neighbors, birth_rules) & (grid == 0)
    survive = np.isin(neighbors, survive_rules) & (grid == 1)
    return (birth | survive).astype(np.uint8)

def draw_standard_grid(screen, grid):
    screen.fill(BLACK, pygame.Rect(0, 0, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y, x] == 1:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
                pygame.draw.rect(screen, YELLOW, rect)

def draw_psychedelic_grid(screen, grid):
    t = pygame.time.get_ticks() / 1000.0
    bg_color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb((t * 0.05) % 1.0, 0.2, 0.07))
    screen.fill(bg_color, pygame.Rect(0, 0, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))

    angle = t * 0.2
    dx, dy = math.cos(angle), math.sin(angle)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y, x] == 1:
                weirdness = math.sin(abs(x * 0.05 + t) ** 1.2) * math.cos(abs(y * 0.05 - t) ** 1.1)
                warp = math.sin(x * 0.1 + y * 0.1 + t * 3) * 0.5
                hue = (0.5 + 0.5 * math.sin(((x * dx + y * dy) * 0.02 + t * 0.5 + weirdness + warp))) % 1.0
                color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(hue, 1, 1))
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
                pygame.draw.rect(screen, color, rect)

def draw_grid(screen, grid, psychedelic_mode):
    if psychedelic_mode:
        draw_psychedelic_grid(screen, grid)
    else:
        draw_standard_grid(screen, grid)


def draw_legend(surface):
    font = pygame.font.SysFont("consolas", 16)
    controls = [
        "Controls:", "[Space]  Pause / Play", "[S]      Step", "[R]      Randomize",
        "[C]      Clear", "[P]      Psychedelic Mode"
    ]
    for i, text in enumerate(controls):
        rendered = font.render(text, True, (200, 200, 200))
        surface.blit(rendered, (10, 10 + i * 20))

def main():
    pygame.init()
    screen_size = (GRID_WIDTH * CELL_SIZE + UI_WIDTH_PIXELS, GRID_HEIGHT * CELL_SIZE)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Conway's Game of Life with pygame_gui")
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager(screen_size)

    # GUI Layout Coordinates
    label_x = GRID_WIDTH * CELL_SIZE + 20
    element_x = label_x + 180

    # UI Components
    pygame_gui.elements.UILabel(pygame.Rect((label_x, 20), (160, 24)), "FPS", manager)
    slider = pygame_gui.elements.UIHorizontalSlider(pygame.Rect((element_x, 20), (160, 24)), INITIAL_FPS, (1, 60), manager)

    pygame_gui.elements.UILabel(pygame.Rect((label_x, 60), (160, 30)), "Pause simulation", manager)
    pause_button = pygame_gui.elements.UIButton(pygame.Rect((element_x, 60), (75, 30)), 'Pause', manager)

    pygame_gui.elements.UILabel(pygame.Rect((label_x, 95), (160, 30)), "Step once", manager)
    step_button = pygame_gui.elements.UIButton(pygame.Rect((element_x, 95), (75, 30)), 'Step', manager)

    pygame_gui.elements.UILabel(pygame.Rect((label_x, 140), (160, 30)), "Rule (e.g. B3/S23)", manager)
    rule_input = pygame_gui.elements.UITextEntryLine(pygame.Rect((element_x, 140), (160, 30)), manager)
    rule_input.set_text(RULE_STRING)

    pygame_gui.elements.UILabel(pygame.Rect((label_x, 180), (160, 30)), "Randomize grid", manager)
    randomize_button = pygame_gui.elements.UIButton(pygame.Rect((element_x, 180), (160, 30)), 'Randomize', manager)

    pygame_gui.elements.UILabel(pygame.Rect((label_x, 220), (160, 30)), "Psychedelic mode", manager)
    psy_button = pygame_gui.elements.UIButton(pygame.Rect((element_x, 220), (160, 30)), "Turn On", manager)

    pygame_gui.elements.UILabel(pygame.Rect((label_x, 260), (160, 30)), "Clear the grid", manager)
    clear_button = pygame_gui.elements.UIButton(pygame.Rect((element_x, 260), (160, 30)), 'Clear Grid', manager)

    # Initial State
    grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])
    birth_rules, survive_rules = parse_rule(RULE_STRING)
    fps = INITIAL_FPS
    sim_interval = 1000 / fps
    time_since_last_step = 0
    paused = False
    step_requested = False
    mouse_down = False
    drawing_value = 1
    psychedelic_mode = False
    running = True

    while running:
        time_delta = clock.tick(60)
        time_since_last_step += time_delta

        for event in pygame.event.get():
            manager.process_events(event)

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if x < GRID_WIDTH * CELL_SIZE and y < GRID_HEIGHT * CELL_SIZE:
                    gx, gy = x // CELL_SIZE, y // CELL_SIZE
                    drawing_value = 1 if grid[gy, gx] == 0 else 0
                    grid[gy, gx] = drawing_value
                    mouse_down = True

            elif event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False

            elif event.type == pygame.MOUSEMOTION and mouse_down:
                x, y = event.pos
                if x < GRID_WIDTH * CELL_SIZE and y < GRID_HEIGHT * CELL_SIZE:
                    gx, gy = x // CELL_SIZE, y // CELL_SIZE
                    grid[gy, gx] = drawing_value

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                    pause_button.set_text("Play" if paused else "Pause")
                elif event.key == pygame.K_s:
                    step_requested = True
                elif event.key == pygame.K_r:
                    grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])
                elif event.key == pygame.K_c:
                    grid[:] = 0
                elif event.key == pygame.K_p:
                    psychedelic_mode = not psychedelic_mode
                    psy_button.set_text("Turn On" if not psychedelic_mode else "Turn Off")

            elif event.type == pygame.USEREVENT:
                if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == pause_button:
                        paused = not paused
                        pause_button.set_text("Play" if paused else "Pause")
                    elif event.ui_element == step_button:
                        step_requested = True
                    elif event.ui_element == randomize_button:
                        grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])
                    elif event.ui_element == clear_button:
                        grid[:] = 0
                    elif event.ui_element == psy_button:
                        psychedelic_mode = not psychedelic_mode
                        psy_button.set_text("Turn On" if not psychedelic_mode else "Turn Off")
                elif event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_element == rule_input:
                    birth_rules, survive_rules = parse_rule(rule_input.get_text())

        manager.update(time_delta / 1000.0)

        if (not paused and time_since_last_step >= sim_interval) or (paused and step_requested):
            grid = update_grid(grid, birth_rules, survive_rules)
            time_since_last_step = 0
            step_requested = False

        fps = int(slider.get_current_value())
        sim_interval = 1000 / fps

        draw_grid(screen, grid, psychedelic_mode)
        manager.draw_ui(screen)
        draw_legend(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
