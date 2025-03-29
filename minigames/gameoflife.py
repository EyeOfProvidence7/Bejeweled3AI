import pygame
import numpy as np
from scipy.signal import convolve2d

# Config
CELL_SIZE = 10
GRID_WIDTH = 160
GRID_HEIGHT = 120
UI_WIDTH_PIXELS = 200
INITIAL_FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
BLUE = (100, 100, 255)

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
    # Define kernel to count 8 neighbors
    kernel = np.array([[1, 1, 1],
                       [1, 0, 1],
                       [1, 1, 1]])
    
    neighbors = convolve2d(grid, kernel, mode='same', boundary='wrap')

    birth = np.isin(neighbors, birth_rules) & (grid == 0)
    survive = np.isin(neighbors, survive_rules) & (grid == 1)

    return (birth | survive).astype(np.uint8)

def draw_grid(screen, grid):
    screen.fill(BLACK, pygame.Rect(0, 0, GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y, x] == 1:
                rect = pygame.Rect(x * CELL_SIZE - 1, y * CELL_SIZE - 1, CELL_SIZE - 1, CELL_SIZE - 1)
                pygame.draw.rect(screen, WHITE, rect)

def draw_ui(screen, fps, slider_rect, slider_handle_x, font, paused, pause_button_rect, step_button_rect):
    ui_x_start = GRID_WIDTH * CELL_SIZE
    screen.fill(BLACK, pygame.Rect(ui_x_start, 0, UI_WIDTH_PIXELS, GRID_HEIGHT * CELL_SIZE))

    # FPS Text
    fps_text = font.render(f"FPS: {fps}", True, WHITE)
    screen.blit(fps_text, (ui_x_start + 20, 20))

    # Slider Bar
    pygame.draw.rect(screen, (200, 200, 200), slider_rect)
    pygame.draw.circle(screen, BLUE, (slider_handle_x, slider_rect.centery), 8)

    # Separator line
    sep_y = slider_rect.bottom + 20
    pygame.draw.line(screen, GRAY, (ui_x_start + 10, sep_y), (ui_x_start + UI_WIDTH_PIXELS - 10, sep_y), 1)

    # Buttons
    pygame.draw.rect(screen, (50, 50, 50), pause_button_rect)
    pygame.draw.rect(screen, (50, 50, 50), step_button_rect)

    pause_text = font.render("Pause" if not paused else "Play", True, WHITE)
    step_text = font.render("Step", True, WHITE)

    screen.blit(pause_text, (pause_button_rect.centerx - pause_text.get_width() // 2,
                             pause_button_rect.centery - pause_text.get_height() // 2))

    screen.blit(step_text, (step_button_rect.centerx - step_text.get_width() // 2,
                            step_button_rect.centery - step_text.get_height() // 2))

def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE + UI_WIDTH_PIXELS, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("Conway's Game of Life with FPS Control")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])
    birth_rules, survive_rules = parse_rule(RULE_STRING)

    slider_rect = pygame.Rect(GRID_WIDTH * CELL_SIZE + 20, 60, 160, 4)
    slider_min_x = slider_rect.left
    slider_max_x = slider_rect.right
    slider_handle_x = int(slider_min_x + (INITIAL_FPS / 60) * (slider_max_x - slider_min_x))
    dragging_slider = False

    pause_button_rect = pygame.Rect(GRID_WIDTH * CELL_SIZE + 20, 100, 75, 30)
    step_button_rect = pygame.Rect(GRID_WIDTH * CELL_SIZE + 105, 100, 75, 30)
    step_requested = False

    fps = INITIAL_FPS
    sim_interval = 1000 / fps  # milliseconds per simulation step
    time_since_last_step = 0

    paused = False
    running = True

    while running:
        dt = clock.tick(60)  # Always render at 60 FPS
        time_since_last_step += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])
                    paused = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if abs(event.pos[1] - slider_rect.centery) < 10 and slider_rect.collidepoint(event.pos):
                        dragging_slider = True
                    elif pause_button_rect.collidepoint(event.pos):
                        paused = not paused
                    elif step_button_rect.collidepoint(event.pos):
                        step_requested = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_slider = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging_slider:
                    slider_handle_x = max(slider_min_x, min(event.pos[0], slider_max_x))
                    relative_pos = (slider_handle_x - slider_min_x) / (slider_max_x - slider_min_x)
                    fps = int(1 + relative_pos * 59)  # FPS range: 1 - 60
                    sim_interval = 1000 / fps

            if (not paused and time_since_last_step >= sim_interval) or (paused and step_requested):
                grid = update_grid(grid, birth_rules, survive_rules)
                time_since_last_step = 0
                step_requested = False


        draw_grid(screen, grid)
        draw_ui(screen, fps, slider_rect, slider_handle_x, font, paused, pause_button_rect, step_button_rect)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
