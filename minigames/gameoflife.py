import pygame
import numpy as np

# Config
CELL_SIZE = 10
GRID_WIDTH = 80
GRID_HEIGHT = 60
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def update_grid(grid):
    new_grid = np.copy(grid)
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            neighbors = np.sum(grid[max(0, y-1):min(y+2, GRID_HEIGHT),
                                    max(0, x-1):min(x+2, GRID_WIDTH)]) - grid[y, x]
            if grid[y, x] == 1 and (neighbors < 2 or neighbors > 3):
                new_grid[y, x] = 0
            elif grid[y, x] == 0 and neighbors == 3:
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
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("Conway's Game of Life")
    clock = pygame.time.Clock()

    grid = np.random.choice([0, 1], size=(GRID_HEIGHT, GRID_WIDTH), p=[0.8, 0.2])

    running = True
    paused = False

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
            grid = update_grid(grid)

        draw_grid(screen, grid)

    pygame.quit()

if __name__ == "__main__":
    main()
