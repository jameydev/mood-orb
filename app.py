import pygame
import math
import sys
import random
import os
import numpy as np
import sounddevice as sd

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

# Aurora ribbons
def draw_aurora():
    for band in range(3):
        points = []
        base_y = HEIGHT // 3 + band * 40
        color = pygame.Color(0)
        color.hsva = ((bg_offset * 2 + band * 60) % 360, 80, 80, 80)
        for x in range(0, WIDTH, 10):
            y = base_y + int(math.sin((x / 80) + bg_offset / 10 + band) * 30)
            points.append((x, y))
        if len(points) > 1:
            pygame.draw.lines(screen, color, False, points, 8)

# Fireflies
fireflies = [{"x": random.uniform(0, WIDTH),
              "y": random.uniform(0, HEIGHT),
              "dx": random.uniform(-0.5, 0.5),
              "dy": random.uniform(-0.5, 0.5),
              "r": random.randint(2, 5),
              "a": random.randint(120, 200)} for _ in range(20)]

def update_and_draw_fireflies():
    for f in fireflies:
        f["x"] += f["dx"] + math.sin(pygame.time.get_ticks() / 1000 + f["r"])
        f["y"] += f["dy"] + math.cos(pygame.time.get_ticks() / 1000 + f["r"])
        if f["x"] < 0: f["x"] = WIDTH
        if f["x"] > WIDTH: f["x"] = 0
        if f["y"] < 0: f["y"] = HEIGHT
        if f["y"] > HEIGHT: f["y"] = 0
        color = (255, 255, 180, f["a"])
        surf = pygame.Surface((f["r"]*4, f["r"]*4), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (f["r"]*2, f["r"]*2), f["r"])
        screen.blit(surf, (f["x"]-f["r"]*2, f["y"]-f["r"]*2))

def regenerate_fireflies():
    global fireflies
    fireflies = [{"x": random.uniform(0, WIDTH),
                  "y": random.uniform(0, HEIGHT),
                  "dx": random.uniform(-0.5, 0.5),
                  "dy": random.uniform(-0.5, 0.5),
                  "r": random.randint(2, 5),
                  "a": random.randint(120, 200)} for _ in range(20)]

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

# Global variable to store audio level
audio_level = 0.0
prev_audio_level = 0.0
spike = 0.0
dominant_freq = 0.0

def audio_callback(indata, frames, time, status):
    global audio_level, dominant_freq
    # Calculate RMS (root mean square) volume
    audio_level = np.sqrt(np.mean(indata**2))
    # FFT for dominant frequency
    fft = np.fft.rfft(indata[:, 0])
    freqs = np.fft.rfftfreq(len(indata), 1/44100)
    idx = np.argmax(np.abs(fft))
    dominant_freq = freqs[idx] if idx < len(freqs) else 0.0
    # print("audio_level:", audio_level, "dominant_freq:", dominant_freq)

# Start audio input stream (try to use default loopback device)
DEVICE_INDEX = 1  # <-- change this to your device index

try:
    stream = sd.InputStream(
        device=DEVICE_INDEX,
        callback=audio_callback,
        channels=1,
        samplerate=44100,
        blocksize=1024
    )
    stream.start()
except Exception as e:
    print("Audio input stream could not be started:", e)
    audio_level = 0.0

start_time = pygame.time.get_ticks()
running = True

# Add this at the top of your file (after other globals)
hue_offset = 0

while running:
    screen.fill((0, 0, 0))
    draw_background()
    update_and_draw_dust()
    if mode == "nebula":
        update_and_draw_stars()
    elif mode == "aurora":
        draw_aurora()
    elif mode == "firefly":
        update_and_draw_fireflies()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), flags)
            regenerate_stars()
            regenerate_dust()
            regenerate_fireflies()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pulse_boost = 1.8

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                mode = "chill"
            elif event.key == pygame.K_2:
                mode = "hyper"
            elif event.key == pygame.K_3:
                mode = "nebula"
            elif event.key == pygame.K_4:
                mode = "aurora"
            elif event.key == pygame.K_5:
                mode = "firefly"
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

    # Smooth audio for less jitter (reduce smoothing for more immediate response)
    smoothed_audio = 0.6 * audio_level + 0.4 * prev_audio_level
    prev_audio_level = smoothed_audio

    # Smooth dominant frequency for less jitter
    smoothed_freq = 0.7 * dominant_freq + 0.3 * (globals().get('prev_freq', 0.0))
    globals()['prev_freq'] = smoothed_freq

    # Map frequency to a pulse effect
    freq_norm = min(max((smoothed_freq - 200) / 1800, 0), 1)  # Normalize to 0-1

    # Dramatic, melody-driven pulse
    pulse = math.sin(elapsed * pulse_speed) * 0.5 + 0.5
    pulse += freq_norm * 8.0  # Increase multiplier for much bigger expansion
    pulse += min(smoothed_audio * 4000, 8)  # Increase audio reactivity

    pulse = max(pulse, 0.5)
    pulse *= pulse_boost
    pulse_boost = max(1.0, pulse_boost - 0.02)

    # Dramatically increase orb and glow size with pulse
    orb_radius = int(min(WIDTH, HEIGHT) // 10 + pulse * (min(WIDTH, HEIGHT) // 3))
    center = (WIDTH // 2, HEIGHT // 2)
    glow_radius = int(orb_radius + pulse * max_glow * 2)  # Glow also expands more

    # --- Melody-driven brightness and opacity ---
    brightness = int(40 + freq_norm * 60)
    orb_alpha = int(100 + freq_norm * 155)
    orb_alpha_hsva = int(orb_alpha * 100 / 255)

    music_threshold = 0.01  # Adjust this threshold as needed for your setup

    if smoothed_audio > music_threshold:
        hue_offset = (hue_offset + 2) % 360  # Increase for faster cycling
        hue = hue_offset
    else:
        hue = int((mouse_pos[0] / WIDTH) * 360) % 360  # fallback to mouse

    # Check if mouse is over the orb
    dist_to_center = math.hypot(mouse_pos[0] - center[0], mouse_pos[1] - center[1])
    if dist_to_center < orb_radius:
        hue = int((mouse_pos[0] / WIDTH) * 360) % 360  # Use mouse position for hue
    else:
        hue_offset = (hue_offset + 2) % 360  # Always cycle
        hue = hue_offset

    orb_color = pygame.Color(0)
    orb_color.hsva = (hue, 100, brightness, orb_alpha_hsva)

    # Draw with new color and alpha
    draw_glow(center, glow_radius, orb_color)
    orb_surface = pygame.Surface((orb_radius*2, orb_radius*2), pygame.SRCALPHA)
    pygame.draw.circle(orb_surface, orb_color, (orb_radius, orb_radius), orb_radius)
    screen.blit(orb_surface, (center[0]-orb_radius, center[1]-orb_radius))
    pygame.draw.circle(screen, (255, 255, 255, 10), center, glow_radius, width=2)

    pygame.display.flip()
    clock.tick(60)

# At the end, stop the stream
try:
    stream.stop()
    stream.close()
except Exception:
    pass

pygame.quit()
sys.exit()
