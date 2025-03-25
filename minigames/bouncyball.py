import pygame
import sys
import random

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Game 1 - Gravity Bouncer with Trippy Trails")
    clock = pygame.time.Clock()

    ball_radius = 20
    ball_x = random.randint(ball_radius, 800 - ball_radius)
    ball_y = random.randint(ball_radius, 600 - ball_radius)
    ball_dx = 4
    ball_dy = 0  # Start with no vertical movement
    gravity = 0.3  # Constant downward acceleration
    bounce_energy_loss = 0.8  # Lose some speed on bounce

    ball_color = (255, 255, 255)  # white

    # Instead of clearing the screen, draw a semi-transparent black rectangle
    trail_surface = pygame.Surface((800, 600), pygame.SRCALPHA)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Apply gravity
        ball_dy += gravity

        # Move ball
        ball_x += ball_dx
        ball_y += ball_dy

        # Bounce off walls
        if ball_x - ball_radius <= 0 or ball_x + ball_radius >= 800:
            ball_dx *= -1

        if ball_y + ball_radius >= 600:
            ball_y = 600 - ball_radius
            ball_dy *= -1
            ball_dy *= bounce_energy_loss  # lose some energy
        elif ball_y - ball_radius <= 0:
            ball_y = ball_radius
            ball_dy *= -1

        # Leave a trail
        trail_surface.fill((0, 0, 0, 20))  # translucent black rectangle
        screen.blit(trail_surface, (0, 0))

        # Draw ball
        pygame.draw.circle(screen, ball_color, (int(ball_x), int(ball_y)), ball_radius)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
