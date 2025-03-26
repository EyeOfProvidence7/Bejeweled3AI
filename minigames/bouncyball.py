import pygame
import sys
import random
import math

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Game 2 - Repelled by Mouse")
    clock = pygame.time.Clock()

    ball_radius = 20
    ball_x = random.randint(ball_radius, 800 - ball_radius)
    ball_y = random.randint(ball_radius, 600 - ball_radius)
    ball_dx = 4
    ball_dy = 0
    gravity = 0.3
    bounce_energy_loss = 0.8

    hue = 0
    trail_surface = pygame.Surface((800, 600), pygame.SRCALPHA)

    repel_strength = 1000  # tweak this to feel right
    min_distance = 20       # clamp to avoid insane speeds

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Apply gravity
        ball_dy += gravity

        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Vector from mouse to ball
        dx = ball_x - mouse_x
        dy = ball_y - mouse_y
        distance_sq = dx ** 2 + dy ** 2
        distance = max(math.sqrt(distance_sq), min_distance)

        # Normalize vector
        nx = dx / distance
        ny = dy / distance

        # Apply repelling force: F = k / r^2
        force = repel_strength / distance_sq
        ball_dx += nx * force
        ball_dy += ny * force

        # Move ball
        ball_x += ball_dx
        ball_y += ball_dy

        # Bounce off walls
        if ball_x - ball_radius <= 0:
            ball_x = ball_radius
            ball_dx *= -1
            ball_dx *= bounce_energy_loss
        elif ball_x + ball_radius >= 800:
            ball_x = 800 - ball_radius
            ball_dx *= -1
            ball_dx *= bounce_energy_loss
        if ball_y + ball_radius >= 600:
            ball_y = 600 - ball_radius
            ball_dy *= -1
            ball_dy *= bounce_energy_loss
        elif ball_y - ball_radius <= 0:
            ball_y = ball_radius
            ball_dy *= -1
            ball_dy *= bounce_energy_loss

        # Update color
        hue = (hue + 1) % 360
        ball_color = pygame.Color(0)
        ball_color.hsva = (hue, 100, 100, 100)

        # Draw trail
        trail_surface.fill((0, 0, 0, 20))
        screen.blit(trail_surface, (0, 0))

        # Draw ball
        pygame.draw.circle(screen, ball_color, (int(ball_x), int(ball_y)), ball_radius)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
