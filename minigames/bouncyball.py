import pygame
import sys
import random

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Game 1 - Bouncy Ball")
    clock = pygame.time.Clock()

    # Ball setup
    ball_radius = 20
    ball_x = random.randint(ball_radius, 800 - ball_radius)
    ball_y = random.randint(ball_radius, 600 - ball_radius)
    ball_dx = 4
    ball_dy = 3
    ball_color = (255, 0, 0)  # red

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Move ball
        ball_x += ball_dx
        ball_y += ball_dy

        # Bounce off walls
        if ball_x - ball_radius <= 0 or ball_x + ball_radius >= 800:
            ball_dx *= -1
        if ball_y - ball_radius <= 0 or ball_y + ball_radius >= 600:
            ball_dy *= -1

        # Draw
        screen.fill((0, 0, 0))  # black background
        pygame.draw.circle(screen, ball_color, (ball_x, ball_y), ball_radius)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
