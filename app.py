import pygame
import math
import sys
import random
import os

pygame.init()
pygame.mixer.init()

# Setup
WIDTH, HEIGHT = 800, 600
flags = pygame.RESIZABLE
screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
is_fullscreen = False
pygame.display.set_caption("🌌 Cosmic Mood Orb")
clock = pygame.time.Clock()

# Load music
if os.path.exists("vibe.mp3"):
    pygame.mixer.music.load("vibe.mp3")
    pygame.mixer.music.play(-1)

# Orb
orb_radius = 100
pulse_speed = 2
max_glow = 100
pulse_boost = 1.0
mode = "chill"
bg_offset = 0

# Starfield
stars = [{"x": random.randint(0, WIDTH),
          "y": random.randint(0, HEIGHT),
          "alpha": random.randint(100, 255),
          "twinkle": random.choice([-1, 1])} for _ in range(100)]

# Space dust
dust = [{"x": random.randint(0, WIDTH),
         "y": random.randint(0, HEIGHT),
         "dx": random.uniform(-0.3, 0.3),
         "dy": random.uniform(-0.3, 0.3),
         "size": random.randint(1, 3)} for _ in range(60)]

def get_color_from_mouse(pos):
    x, y = pos
    hue = int((x / WIDTH) * 360) % 360
    color = pygame.Color(0)
    color.hsva = (hue, 100, 100, 100)
    return color

def draw_background():
    global bg_offset
    for y in range(0, HEIGHT, 10):
        hue = (bg_offset + y) % 360
        color = pygame.Color(0)
        color.hsva = (hue, 60, 15, 100)
        pygame.draw.rect(screen, color, pygame.Rect(0, y, WIDTH, 10))
    bg_offset += 0.2 if mode == "chill" else 1.2

def draw_glow(center, base_radius, color, intensity=5):
    for i in range(intensity, 0, -1):
        alpha = int(255 * (i / intensity)**2)
        glow_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        glow_color = (*color[:3], alpha // 3)
        pygame.draw.circle(glow_surface, glow_color, center, base_radius + i * 15)
        screen.blit(glow_surface, (0, 0))

def update_and_draw_dust():
    for d in dust:
        d["x"] += d["dx"]
        d["y"] += d["dy"]
        if d["x"] < 0: d["x"] = WIDTH
        if d["x"] > WIDTH: d["x"] = 0
        if d["y"] < 0: d["y"] = HEIGHT
        if d["y"] > HEIGHT: d["y"] = 0
        pygame.draw.circle(screen, (200, 200, 255), (int(d["x"]), int(d["y"])), d["size"])

def update_and_draw_stars():
    for s in stars:
        s["alpha"] += s["twinkle"] * random.randint(1, 3)

        # Clamp alpha to safe range
        s["alpha"] = max(100, min(255, s["alpha"]))
        if s["alpha"] in (100, 255):
            s["twinkle"] *= -1

        # Draw twinkling star
        star_surface = pygame.Surface((2, 2), pygame.SRCALPHA)
        star_surface.fill((255, 255, 255, s["alpha"]))
        screen.blit(star_surface, (s["x"], s["y"]))

def regenerate_stars():
    global stars
    stars = [{"x": random.randint(0, WIDTH),
              "y": random.randint(0, HEIGHT),
              "alpha": random.randint(100, 255),
              "twinkle": random.choice([-1, 1])} for _ in range(100)]

def regenerate_dust():
    global dust
    dust = [{"x": random.randint(0, WIDTH),
             "y": random.randint(0, HEIGHT),
             "dx": random.uniform(-0.3, 0.3),
             "dy": random.uniform(-0.3, 0.3),
             "size": random.randint(1, 3)} for _ in range(60)]



start_time = pygame.time.get_ticks()
running = True

while running:
    screen.fill((0, 0, 0))
    draw_background()
    update_and_draw_dust()
    if mode == "nebula":
        update_and_draw_stars()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
            regenerate_stars()
            regenerate_dust()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pulse_boost = 1.8

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                mode = "chill"
            elif event.key == pygame.K_2:
                mode = "hyper"
            elif event.key == pygame.K_3:
                mode = "nebula"
            elif event.key == pygame.K_s:
                pygame.image.save(screen, f"screenshot_{pygame.time.get_ticks()}.png")
            if event.key == pygame.K_f:
                is_fullscreen = not is_fullscreen
                if is_fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    WIDTH, HEIGHT = screen.get_size()
                else:
                    screen = pygame.display.set_mode((800, 600), flags)
                    WIDTH, HEIGHT = 800, 600
            elif event.key == pygame.K_ESCAPE:
                if is_fullscreen:
                    is_fullscreen = False
                    screen = pygame.display.set_mode((800, 600), flags)
                    WIDTH, HEIGHT = 800, 600
                else:
                    running = False


    mouse_pos = pygame.mouse.get_pos()
    elapsed = (pygame.time.get_ticks() - start_time) / 1000
    pulse = math.sin(elapsed * pulse_speed) * 0.5 + 0.5
    pulse *= pulse_boost
    pulse_boost = max(1.0, pulse_boost - 0.02)

    # Orb radius and center scale with window size
    orb_radius = min(WIDTH, HEIGHT) // 8
    center = (WIDTH // 2, HEIGHT // 2)
    glow_radius = int(orb_radius + pulse * max_glow)

    orb_color = get_color_from_mouse(mouse_pos)

    draw_glow(center, glow_radius, orb_color)
    pygame.draw.circle(screen, orb_color, center, orb_radius)
    pygame.draw.circle(screen, (255, 255, 255, 10), center, glow_radius, width=2)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
