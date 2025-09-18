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
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput", "pystray", "Pillow"])
    from pynput import mouse, keyboard
    import pystray
    from PIL import Image

# ------------------------
# Configuration
# ------------------------
active = True
left_pressed = False
right_pressed = False
running = True
tick_ms = 14
base_vertical = 2

mouse_controller = mouse.Controller()

# ------------------------
# Progressive vertical movement logic
# ------------------------
def vertical_motion_loop():
    global left_pressed, right_pressed, active, running
    while running:
        if active and left_pressed and right_pressed:
            start_time = time.time()
            while running and left_pressed and right_pressed:
                elapsed = time.time() - start_time
                # Determine vertical strength
                if elapsed < 1:
                    vertical_strength = 3
                elif elapsed < 3:
                    vertical_strength = 8
                elif elapsed < 6:
                    vertical_strength = 10
                elif elapsed < 10:
                    vertical_strength = 12
                else:
                    vertical_strength = 12
                # Move vertically only
                mouse_controller.move(0, vertical_strength)
                time.sleep(tick_ms / 1000.0)
        else:
            time.sleep(0.01)

threading.Thread(target=vertical_motion_loop, daemon=True).start()

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
icon_image = Image.new('RGB', (64, 64), (50, 50, 50))  # simple gray square
icon = pystray.Icon("VerticalMover", icon_image, "Vertical Motion", menu=pystray.Menu(
    pystray.MenuItem("Exit", lambda icon, item: (setattr(sys.modules[__name__], 'running', False), icon.stop()))
))
threading.Thread(target=icon.run, daemon=True).start()

# ------------------------
# Keep script alive
# ------------------------
while running:
    time.sleep(0.2)
