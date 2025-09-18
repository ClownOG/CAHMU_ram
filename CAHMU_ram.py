#!/usr/bin/env python3
"""
RAM-Executable Smooth Motion Script
- Single instance
- Progressive vertical/horizontal movement
- Tray icon
- No logs or temporary files
"""

import sys
import threading
import time
import ctypes

# ------------------------
# Single-instance check
# ------------------------
mutex = ctypes.windll.kernel32.CreateMutexW(None, ctypes.c_bool(True), "CAHMU_SINGLE_INSTANCE_MUTEX")
if ctypes.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
    sys.exit(0)

# ------------------------
# Dependencies
# ------------------------
try:
    import pynput
    from pynput import mouse, keyboard
    import pystray
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput", "pystray", "Pillow"])
    import pynput
    from pynput import mouse, keyboard
    import pystray
    from PIL import Image

# ------------------------
# Configuration
# ------------------------
modes = [{"verticalStrength": 2, "horizontalStrength": -1, "description": "default"}]
selected_mode_index = 0
active = True
tick_ms = 14
base_vertical = 2
max_vertical = 50

left_pressed = False
right_pressed = False
running = True

mouse_controller = mouse.Controller()

# ------------------------
# Movement logic
# ------------------------
def move_cursor(dx, dy):
    mouse_controller.move(dx, dy)

def motion_loop():
    global left_pressed, right_pressed, active, selected_mode_index, running
    while running:
        if active and left_pressed and right_pressed:
            mode = modes[selected_mode_index]
            start_time = time.time()
            while running and left_pressed and right_pressed:
                elapsed = time.time() - start_time
                vertical_strength = base_vertical
                if elapsed >= 0.75:
                    vertical_strength = 3 + ((elapsed - 0.75)//0.35)*1.25
                if vertical_strength > max_vertical:
                    vertical_strength = max_vertical
                dy = vertical_strength
                dx = mode["horizontalStrength"] * (vertical_strength / 3)
                move_cursor(dx, dy)
                time.sleep(tick_ms / 1000.0)
        else:
            time.sleep(0.01)

threading.Thread(target=motion_loop, daemon=True).start()

# ------------------------
# Mouse listener
# ------------------------
def on_click(x, y, button, pressed):
    global left_pressed, right_pressed, active, selected_mode_index
    if button == mouse.Button.left:
        left_pressed = pressed
    elif button == mouse.Button.right:
        right_pressed = pressed
    elif button == mouse.Button.x1 and pressed:
        selected_mode_index = (selected_mode_index + 1) % len(modes)
    elif button == mouse.Button.x2 and pressed:
        active = not active

mouse.Listener(on_click=on_click).start()

# ------------------------
# Keyboard listener
# ------------------------
def on_press(key):
    global active, selected_mode_index, running
    if key == keyboard.Key.f9:
        active = not active
    elif key == keyboard.Key.f8:
        selected_mode_index = (selected_mode_index + 1) % len(modes)
    elif key == keyboard.Key.esc:
        running = False
        icon.stop()
        return False

keyboard.Listener(on_press=on_press).start()

# ------------------------
# System tray
# ------------------------
icon_image = Image.new('RGB', (64, 64), (50, 50, 50))  # simple gray square
icon = pystray.Icon("SmoothMover", icon_image, "Smooth Motion", menu=pystray.Menu(
    pystray.MenuItem("Exit", lambda icon, item: (setattr(sys.modules[__name__], 'running', False), icon.stop()))
))
threading.Thread(target=icon.run, daemon=True).start()

# ------------------------
# Keep script alive
# ------------------------
while running:
    time.sleep(0.2)
