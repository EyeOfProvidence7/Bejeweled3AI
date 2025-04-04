import pygame
import pygame_gui
import numpy as np
from scipy.signal import convolve2d
import colorsys
import math

# Config
#-----------------------------
# Fixed Screen Resolution
TOTAL_WIDTH = 1600
TOTAL_HEIGHT = 1200

# Start with initial grid width and calculate from that
INITIAL_GRID_WIDTH = 160
CELL_SIZE = TOTAL_WIDTH // INITIAL_GRID_WIDTH
GRID_WIDTH = TOTAL_WIDTH // CELL_SIZE
GRID_HEIGHT = TOTAL_HEIGHT // CELL_SIZE
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


def draw_standard_grid(screen, grid):
    global CELL_SIZE, GRID_WIDTH, GRID_HEIGHT

    if GRID_WIDTH > INITIAL_GRID_WIDTH:
        padding = 0
    else:
        padding = 1

    screen.fill(BLACK, pygame.Rect(0, 0, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y, x] == 1:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - padding, CELL_SIZE - padding)
                pygame.draw.rect(screen, YELLOW, rect)


def draw_psychedelic_grid(screen, grid):
    global CELL_SIZE, GRID_WIDTH, GRID_HEIGHT

    if GRID_WIDTH > INITIAL_GRID_WIDTH:
        padding = 0
    else:
        padding = 1

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
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - padding, CELL_SIZE - padding)
                pygame.draw.rect(screen, color, rect)


def draw_grid(screen, grid, psychedelic_mode):
    if psychedelic_mode:
        draw_psychedelic_grid(screen, grid)
    else:
        draw_standard_grid(screen, grid)


def draw_legend(surface):
    font = pygame.font.SysFont("consolas", 16)
    lines = [
        "Controls:",
        "[Space]  Pause / Play",
        "[S]      Step",
        "[R]      Randomize",
        "[C]      Clear",
        "[P]      Psychedelic Mode",
    ]
    for i, text in enumerate(lines):
        rendered = font.render(text, True, (200, 200, 200))
        surface.blit(rendered, (10, 10 + i * 20))


def init_pygame_and_ui():
    global GRID_WIDTH, GRID_HEIGHT, CELL_SIZE

    pygame.init()
    screen_size = (GRID_WIDTH * CELL_SIZE + UI_WIDTH_PIXELS, GRID_HEIGHT * CELL_SIZE)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Conway's Game of Life with pygame_gui")
    clock = pygame.time.Clock()
    manager = pygame_gui.UIManager(screen_size)
    return screen, manager, clock


def create_ui_elements(manager):
    global GRID_WIDTH, GRID_HEIGHT, CELL_SIZE

    def rect(x, y, w, h): return pygame.Rect((x, y), (w, h))

    label_x = GRID_WIDTH * CELL_SIZE + 20
    element_x = label_x + 180

    pygame_gui.elements.UILabel(rect(label_x, 340, 160, 30), "Grid Width", manager)
    grid_slider = pygame_gui.elements.UIHorizontalSlider(rect(element_x, 340, 160, 30), INITIAL_GRID_WIDTH, (10, 320), manager)

    pygame_gui.elements.UILabel(rect(label_x, 20, 160, 24), "FPS", manager)
    slider = pygame_gui.elements.UIHorizontalSlider(rect(element_x, 20, 160, 24), INITIAL_FPS, (1, 60), manager)

    pygame_gui.elements.UILabel(rect(label_x, 60, 160, 30), "Pause simulation", manager)
    pause_button = pygame_gui.elements.UIButton(rect(element_x, 60, 75, 30), 'Pause', manager)

    pygame_gui.elements.UILabel(rect(label_x, 95, 160, 30), "Step once", manager)
    step_button = pygame_gui.elements.UIButton(rect(element_x, 95, 75, 30), 'Step', manager)

    pygame_gui.elements.UILabel(rect(label_x, 140, 160, 30), "Rule (e.g. B3/S23)", manager)
    rule_input = pygame_gui.elements.UITextEntryLine(rect(element_x, 140, 160, 30), manager)
    rule_input.set_text(RULE_STRING)

    pygame_gui.elements.UILabel(rect(label_x, 180, 160, 30), "Randomize grid", manager)
    randomize_button = pygame_gui.elements.UIButton(rect(element_x, 180, 160, 30), 'Randomize', manager)

    pygame_gui.elements.UILabel(rect(label_x, 220, 160, 30), "Psychedelic mode", manager)
    psy_button = pygame_gui.elements.UIButton(rect(element_x, 220, 160, 30), "Turn On", manager)

    pygame_gui.elements.UILabel(rect(label_x, 260, 160, 30), "Clear the grid", manager)
    clear_button = pygame_gui.elements.UIButton(rect(element_x, 260, 160, 30), 'Clear Grid', manager)

    pygame_gui.elements.UILabel(rect(label_x, 300, 160, 30), "Brush size", manager)
    brush_slider = pygame_gui.elements.UIHorizontalSlider(rect(element_x, 300, 160, 30), 0, (0, 10), manager)

    return {
        'slider': slider,
        'pause_button': pause_button,
        'step_button': step_button,
        'rule_input': rule_input,
        'randomize_button': randomize_button,
        'psy_button': psy_button,
        'clear_button': clear_button,
        'brush_slider': brush_slider,
        'grid_slider': grid_slider
    }


def apply_brush(grid, cx, cy, value, radius):
    global GRID_WIDTH, GRID_HEIGHT

    for y in range(cy - radius, cy + radius + 1):
        for x in range(cx - radius, cx + radius + 1):
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius ** 2:
                    grid[y, x] = value


def handle_input(event, ui, grid, paused, step_requested, psychedelic_mode,
                 mouse_down, drawing_value, birth_rules, survive_rules):
    global GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, INITIAL_FPS, RULE_STRING

    running = True

    if event.type == pygame.QUIT:
        return False, paused, step_requested, psychedelic_mode, grid, mouse_down, drawing_value, birth_rules, survive_rules

    elif event.type == pygame.MOUSEBUTTONDOWN:
        x, y = event.pos
        if x < GRID_WIDTH * CELL_SIZE and y < GRID_HEIGHT * CELL_SIZE:
            gx, gy = x // CELL_SIZE, y // CELL_SIZE
            brush_size = int(ui['brush_slider'].get_current_value())
            apply_brush(grid, gx, gy, drawing_value, brush_size)
            mouse_down = True

    elif event.type == pygame.MOUSEBUTTONUP:
        mouse_down = False

    elif event.type == pygame.MOUSEMOTION and mouse_down:
        x, y = event.pos
        if x < GRID_WIDTH * CELL_SIZE and y < GRID_HEIGHT * CELL_SIZE:
            gx, gy = x // CELL_SIZE, y // CELL_SIZE
            brush_size = int(ui['brush_slider'].get_current_value())
            apply_brush(grid, gx, gy, drawing_value, brush_size)

    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE:
            paused = not paused
            ui['pause_button'].set_text("Play" if paused else "Pause")
        elif event.key == pygame.K_s:
            step_requested = True
        elif event.key == pygame.K_r:
            grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])
        elif event.key == pygame.K_c:
            grid[:] = 0
        elif event.key == pygame.K_p:
            psychedelic_mode = not psychedelic_mode
            ui['psy_button'].set_text("Turn On" if not psychedelic_mode else "Turn Off")

    elif event.type == pygame.USEREVENT:
        if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == ui['pause_button']:
                paused = not paused
                ui['pause_button'].set_text("Play" if paused else "Pause")
            elif event.ui_element == ui['step_button']:
                step_requested = True
            elif event.ui_element == ui['randomize_button']:
                grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])
            elif event.ui_element == ui['clear_button']:
                grid[:] = 0
            elif event.ui_element == ui['psy_button']:
                psychedelic_mode = not psychedelic_mode
                ui['psy_button'].set_text("Turn On" if not psychedelic_mode else "Turn Off")
        elif event.user_type == pygame_gui.UI_TEXT_ENTRY_FINISHED and event.ui_element == ui['rule_input']:
            birth_rules, survive_rules = parse_rule(ui['rule_input'].get_text())

    return running, paused, step_requested, psychedelic_mode, grid, mouse_down, drawing_value, birth_rules, survive_rules


def draw_fill_preview(screen, ui, mouse_pos):
    global GRID_WIDTH, GRID_HEIGHT, CELL_SIZE


    if mouse_pos[0] < GRID_WIDTH * CELL_SIZE and mouse_pos[1] < GRID_HEIGHT * CELL_SIZE:
        brush_size = int(ui['brush_slider'].get_current_value())
        gx, gy = mouse_pos[0] // CELL_SIZE, mouse_pos[1] // CELL_SIZE

        for y in range(gy - brush_size, gy + brush_size + 1):
            for x in range(gx - brush_size, gx + brush_size + 1):
                if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                    if (x - gx) ** 2 + (y - gy) ** 2 <= brush_size ** 2:
                        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE - 1, CELL_SIZE - 1)
                        pygame.draw.rect(screen, (100, 100, 255), rect, width=1)


def main():
    global GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, INITIAL_FPS, RULE_STRING

    screen, manager, clock = init_pygame_and_ui()
    ui = create_ui_elements(manager)

    grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])
    birth_rules, survive_rules = parse_rule(RULE_STRING)

    grid_slider_value = int(ui['grid_slider'].get_current_value())
    prev_grid_slider_value = grid_slider_value

    fps = INITIAL_FPS
    sim_interval = 1000 / fps
    time_since_last_step = 0
    paused = False
    step_requested = False
    mouse_down = False
    drawing_value = 1
    psychedelic_mode = False
    running = True
    mouse_pos = (0, 0)


    while running:
        time_delta = clock.tick(60)
        time_since_last_step += time_delta
        mouse_pos = pygame.mouse.get_pos()


        for event in pygame.event.get():
            manager.process_events(event)
            running, paused, step_requested, psychedelic_mode, grid, mouse_down, drawing_value, birth_rules, survive_rules = handle_input(
                event, ui, grid, paused, step_requested, psychedelic_mode, mouse_down, drawing_value, birth_rules, survive_rules
            )

        manager.update(time_delta / 1000.0)

        grid_slider_value = int(ui['grid_slider'].get_current_value())
        if grid_slider_value != prev_grid_slider_value:
            # Recalculate dimensions
            CELL_SIZE = TOTAL_WIDTH // grid_slider_value
            GRID_WIDTH = TOTAL_WIDTH // CELL_SIZE
            GRID_HEIGHT = TOTAL_HEIGHT // CELL_SIZE

            # Create a new grid with updated size
            new_grid = np.zeros((GRID_HEIGHT, GRID_WIDTH), dtype=np.uint8)

            # Optionally copy existing grid data into new one
            min_height = min(GRID_HEIGHT, grid.shape[0])
            min_width = min(GRID_WIDTH, grid.shape[1])
            new_grid[:min_height, :min_width] = grid[:min_height, :min_width]

            grid = new_grid
            prev_grid_slider_value = grid_slider_value


        if (not paused and time_since_last_step >= sim_interval) or (paused and step_requested):
            grid = update_grid(grid, birth_rules, survive_rules)
            time_since_last_step = 0
            step_requested = False

        fps = int(ui['slider'].get_current_value())
        sim_interval = 1000 / fps

        draw_grid(screen, grid, psychedelic_mode)
        manager.draw_ui(screen)
        draw_legend(screen)
        draw_fill_preview(screen, ui, mouse_pos)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
