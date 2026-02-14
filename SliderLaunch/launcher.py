import pygame
import sys
import configparser
import subprocess
import math
import time
import win32api

slidershim_path = r'C:\Program Files\slidershim\slidershim.exe'
AUTO_LAUNCH_DELAY = 30000
screen_width = 1920
screen_height = 1080
title_text = "GROUND SLIDER LAUNCHER"

#init
pygame.init()
slidershim_process = None
try:
    print(f"Launching on startup: {slidershim_path}")
    slidershim_process = subprocess.Popen([slidershim_path])
except FileNotFoundError:
    print(f"Startup Error: Executable not found at '{slidershim_path}'")
except Exception as e:
    print(f"An error occurred during startup launch: {e}")
print("Launching slidershim")
time.sleep(2)
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption('Launcher')
black = (0, 0, 0)
white = (255, 255, 255)
try:
    font = pygame.font.Font('font.ttf', 24)
    countdown_font = pygame.font.Font('font.ttf', 24)
except FileNotFoundError:
    font = pygame.font.Font(None, 65)
    countdown_font = pygame.font.Font(None, 40)
try:
    background_image = pygame.image.load('background.png').convert()
    background_image = pygame.transform.scale(background_image, (screen_width, screen_height))
except pygame.error:
    background_image = pygame.Surface((screen_width, screen_height))
    background_image.fill(black)
last_interaction_time = pygame.time.get_ticks()
timer_active = True
config = configparser.ConfigParser()
config.optionxform = str
config.read('games.ini')
try:
    game_data = dict(config['Games'])
except KeyError:
    game_data = {"Error": "Missing games.ini"}
menu_options = list(game_data.keys())
selected_option = 0


def launch_program(path, slidershim_process_to_terminate):
    command = []
    creation_flags = 0
    if path.lower().endswith('.bat'):
        command = ['cmd', '/c', path]
        creation_flags = subprocess.CREATE_NEW_CONSOLE
    else:
        command = [path]
    try:
        if slidershim_process_to_terminate:
            slidershim_process_to_terminate.terminate()
        subprocess.Popen(command, creationflags=creation_flags)
        return False
    except Exception as e:
        print(f"Error launching '{path}': {e}")
        return True

def draw_menu(surface, options, selected, idle_time_ms, is_timer_active):
    surface.blit(background_image, (0, 0))

    title_surface = font.render(title_text, True, white)
    title_rect = title_surface.get_rect(center=(screen_width / 2, 80))
    surface.blit(title_surface, title_rect)

    # --- SCROLLING & LAYOUT CONFIGURATION ---
    start_y = 180
    start_x = 250
    line_spacing = 28
    max_visible = 25  # Maximum number of items to show on screen at once
    
    # Scrollbar visual settings
    scrollbar_x = start_x - 30      # 30 pixels to the left of the text
    scrollbar_width = 8             # Thickness of the scrollbar
    track_color = (50, 50, 50)      # Dark gray for the background track
    thumb_color = (200, 200, 200)   # Light gray for the moving indicator
    # ----------------------------------------

    total_items = len(options)

    # Calculate the scroll offset to keep the selected item visible
    offset = 0
    if selected >= max_visible:
        offset = selected - (max_visible - 1)

    # --- NEW: Draw the Scrollbar ---
    if total_items > max_visible:
        # 1. Draw the background track
        scrollbar_total_height = max_visible * line_spacing
        track_rect = pygame.Rect(scrollbar_x, start_y, scrollbar_width, scrollbar_total_height)
        pygame.draw.rect(surface, track_color, track_rect)
        
        # 2. Calculate thumb height (proportional to visible items)
        # Ensure it never gets smaller than 20 pixels so it's always visible
        thumb_height = max(20, (max_visible / total_items) * scrollbar_total_height)
        
        # 3. Calculate thumb position based on scroll progress
        max_offset = total_items - max_visible
        scroll_percent = offset / max_offset
        
        # The thumb's Y position moves down the track based on percentage
        thumb_y = start_y + (scroll_percent * (scrollbar_total_height - thumb_height))
        
        # 4. Draw the thumb indicator
        thumb_rect = pygame.Rect(scrollbar_x, thumb_y, scrollbar_width, thumb_height)
        pygame.draw.rect(surface, thumb_color, thumb_rect)

    # Draw the menu text
    for i in range(total_items):
        # Calculate where this item sits relative to our scroll window
        relative_index = i - offset
        
        # Only draw the item if it falls within the visible range
        if 0 <= relative_index < max_visible:
            option = options[i]
            display_text = f">> {option}" if i == selected else f"   {option}"
            text_surface = font.render(display_text, True, white)
            
            # Position relative to the top of the menu area
            current_y = start_y + (relative_index * line_spacing)
            text_rect = text_surface.get_rect(topleft=(start_x, current_y))
            surface.blit(text_surface, text_rect)
        
    if is_timer_active and options:
        seconds_left = max(0, math.ceil((AUTO_LAUNCH_DELAY - idle_time_ms) / 1000))
        first_option_name = options[0]
        countdown_text = f"Launching {first_option_name} in {seconds_left} seconds"
        countdown_surface = countdown_font.render(countdown_text, True, white)
        
        text_rect = countdown_surface.get_rect(center=(screen_width / 2, screen_height - 130))
        surface.blit(countdown_surface, text_rect)


# VK Codes 
VK_UP = 0x26
VK_DOWN = 0x28
VK_RETURN = 0x0D # Enter key
VK_COMMA = 0xBC # Comma key
VK_ESCAPE = 0x1B

running = True
idle_time = 0
input_cooldown = 150
last_input_time = 0

while running:
    current_time = pygame.time.get_ticks()
    # (The timer and auto-launch logic remains the same)
    if timer_active:
        idle_time = current_time - last_interaction_time
        if idle_time >= AUTO_LAUNCH_DELAY and menu_options:
            executable_path = game_data.get(menu_options[0])
            if executable_path:
                running = launch_program(executable_path, slidershim_process)

    # This still handles the window closing event
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Replaced keyboard with pywin32 for input handling
    if current_time - last_input_time > input_cooldown:
        # Check for UP keys
        if any(win32api.GetAsyncKeyState(code) for code in [VK_UP, ord('A'), ord('Z'), ord('S')]):
            selected_option = (selected_option - 1) % len(menu_options)
            last_input_time = current_time
            if timer_active: timer_active = False
        
        # Check for DOWN keys
        elif any(win32api.GetAsyncKeyState(code) for code in [VK_DOWN, ord('X'), ord('D'), ord('C')]):
            selected_option = (selected_option + 1) % len(menu_options)
            last_input_time = current_time
            if timer_active: timer_active = False

        # Check for SELECT keys
        elif any(win32api.GetAsyncKeyState(code) for code in [VK_RETURN, ord('J'), ord('M'), ord('K'), VK_COMMA]):
            chosen_option_name = menu_options[selected_option]
            executable_path = game_data.get(chosen_option_name)
            if executable_path:
                running = launch_program(executable_path, slidershim_process)
            last_input_time = current_time
            if timer_active: timer_active = False
    
    # Check for ESCAPE key to quit
    if win32api.GetAsyncKeyState(VK_ESCAPE):
        running = False
    
    if running:
        draw_menu(screen, menu_options, selected_option, idle_time, timer_active)
        pygame.display.flip()

if slidershim_process:
    slidershim_process.terminate()

pygame.quit()