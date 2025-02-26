import pygame
import math

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
BACKGROUND_COLOR = (0, 0, 0)
BALL_COLOR = (255, 0, 0)
HEX_COLOR = (0, 255, 0)

gravity = 0.2
friction = 0.99
bounce_strength = -5  # Strength of bounce when clicking

# Mutable properties
num_vertices = 8  # Number of polygon vertices
num_balls = 2  # Number of balls
ball_radius = 10  # Ball size
rotation_speed = 0.02  # Polygon rotation speed

# Ball properties
balls = [{'x': WIDTH // 2, 'y': HEIGHT // 2 - 100, 'vx': 2, 'vy': 0} for _ in range(num_balls)]

# Polygon properties
polygon_radius = 200
angle = 0

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True

def get_polygon_points(cx, cy, radius, angle, vertices):
    points = []
    for i in range(vertices):
        theta = angle + (2 * math.pi / vertices) * i
        x = cx + radius * math.cos(theta)
        y = cy + radius * math.sin(theta)
        points.append((x, y))
    return points

def reflect_vector(vx, vy, normal_x, normal_y):
    dot = vx * normal_x + vy * normal_y
    reflect_vx = vx - 2 * dot * normal_x
    reflect_vy = vy - 2 * dot * normal_y
    return reflect_vx * friction, reflect_vy * friction

while running:
    screen.fill(BACKGROUND_COLOR)
    angle += rotation_speed
    
    # Get polygon points
    polygon_points = get_polygon_points(WIDTH // 2, HEIGHT // 2, polygon_radius, angle, num_vertices)
    pygame.draw.polygon(screen, HEX_COLOR, polygon_points, 2)
    
    # Update and draw balls
    for ball in balls:
        ball['vy'] += gravity  # Gravity effect
        ball['x'] += ball['vx']
        ball['y'] += ball['vy']
        
        # Ball collision with polygon walls
        for i in range(num_vertices):
            x1, y1 = polygon_points[i]
            x2, y2 = polygon_points[(i + 1) % num_vertices]
            
            # Compute edge normal
            edge_dx, edge_dy = x2 - x1, y2 - y1
            edge_length = math.sqrt(edge_dx**2 + edge_dy**2)
            normal_x, normal_y = -edge_dy / edge_length, edge_dx / edge_length
            
            # Check distance from ball to edge
            edge_to_ball_x = ball['x'] - x1
            edge_to_ball_y = ball['y'] - y1
            dist_to_edge = abs(edge_to_ball_x * normal_x + edge_to_ball_y * normal_y)
            
            if dist_to_edge < ball_radius:
                # Reflect ball velocity
                ball['vx'], ball['vy'] = reflect_vector(ball['vx'], ball['vy'], normal_x, normal_y)
                # Move ball slightly away from wall to prevent sticking
                ball['x'] += normal_x * (ball_radius - dist_to_edge)
                ball['y'] += normal_y * (ball_radius - dist_to_edge)
        
        pygame.draw.circle(screen, BALL_COLOR, (int(ball['x']), int(ball['y'])), ball_radius)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            #for ball in balls:
                #ball['vy'] = bounce_strength  # Apply bounce when mouse is clicked
            #gravity = -gravity
            balls.append({'x': WIDTH // 2, 'y': HEIGHT // 2 - 100, 'vx': 2, 'vy': 0})
        elif event.type == pygame.KEYDOWN:
            gravity = -gravity
    
    pygame.display.flip()
    clock.tick(100)

pygame.quit()
