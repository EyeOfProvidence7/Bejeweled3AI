import pygame
import numpy as np

# Config
CELL_SIZE = 10
GRID_WIDTH = 160
GRID_HEIGHT = 120
UI_WIDTH_PIXELS = 200
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

RULE_STRING = "B3/S23"

def parse_rule(rule_str):
    birth = []
    survive = []

    # Clean and normalize the rule string (e.g., remove whitespace, make uppercase)
    rule_str = rule_str.strip().upper()

    if "B" in rule_str and "S" in rule_str:
        b_section = rule_str.split("S")[0].replace("B", "").replace("/", "")
        s_section = rule_str.split("S")[1].replace("/", "")

        birth = [int(n) for n in b_section if n.isdigit()]
        survive = [int(n) for n in s_section if n.isdigit()]

    return birth, survive


def update_grid(grid, birth_rules, survive_rules):
    new_grid = np.copy(grid)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            neighbors = np.sum(grid[max(0, y-1):min(y+2, GRID_HEIGHT),
                                    max(0, x-1):min(x+2, GRID_WIDTH)]) - grid[y, x]

            if grid[y, x] == 1:
                if neighbors not in survive_rules:
                    new_grid[y, x] = 0
            else:
                if neighbors in birth_rules:
                    new_grid[y, x] = 1
    return new_grid


def draw_grid(screen, grid):
    screen.fill(BLACK)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y, x] == 1:
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, WHITE, rect)
    pygame.display.flip()

def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE + UI_WIDTH_PIXELS, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()

    grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])

    running = True
    paused = False

    birth_rules, survive_rules = parse_rule(RULE_STRING)

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])
                    paused = False

        if not paused:
            grid = update_grid(grid, birth_rules, survive_rules)

        draw_grid(screen, grid)

    pygame.quit()

if __name__ == "__main__":
    main()
