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
    from pynput import mouse, keyboard
    import pystray
    from PIL import Image
    import pyautogui
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput", "pystray", "Pillow", "pyautogui"])
    from pynput import mouse, keyboard
    import pystray
    from PIL import Image
    import pyautogui

# ------------------------
# Configuration
# ------------------------
active = True
left_pressed = False
right_pressed = False
running = True
tick_ms = 14
screen_width, screen_height = 1366, 768
mid_x, mid_y = screen_width // 2, screen_height // 2

# ------------------------
# Vertical stabilization + optional pull logic
# ------------------------
def stabilize_loop():
    global left_pressed, right_pressed, active, running
    while running:
        if active and left_pressed and right_pressed:
            start_time = time.time()
            while running and left_pressed and right_pressed:
                elapsed = time.time() - start_time

                # Determine vertical pull strength
                if elapsed <= 0.5:
                    pull_strength = 3
                elif elapsed <= 3:
                    pull_strength = 6
                else:
                    pull_strength = 9

                # Get current mouse position
                x, y = pyautogui.position()
                delta_y = mid_y - y

                # Move cursor vertically to middle + apply pull strength
                move_y = delta_y * 0.5 + pull_strength  # fraction for smoother correction
                pyautogui.moveRel(0, move_y)

                time.sleep(tick_ms / 1000.0)
        else:
            time.sleep(0.01)

threading.Thread(target=stabilize_loop, daemon=True).start()

# ------------------------
# Mouse listener
# ------------------------
def on_click(x, y, button, pressed):
    global left_pressed, right_pressed, active
    if button == mouse.Button.left:
        left_pressed = pressed
    elif button == mouse.Button.right:
        right_pressed = pressed
    elif button == mouse.Button.x2 and pressed:
        active = not active

mouse.Listener(on_click=on_click).start()

# ------------------------
# Keyboard listener
# ------------------------
def on_press(key):
    global active, running
    if key == keyboard.Key.f9:
        active = not active
    elif key == keyboard.Key.esc:
        running = False
        icon.stop()
        return False

keyboard.Listener(on_press=on_press).start()

# ------------------------
# System tray
# ------------------------
icon_image = Image.new('RGB', (64, 64), (50, 50, 50))  # gray square
icon = pystray.Icon("VerticalStabilizer", icon_image, "Aim Stabilizer", menu=pystray.Menu(
    pystray.MenuItem("Exit", lambda icon, item: (setattr(sys.modules[__name__], 'running', False), icon.stop()))
))
threading.Thread(target=icon.run, daemon=True).start()

# ------------------------
# Keep script alive
# ------------------------
while running:
    time.sleep(0.2)
