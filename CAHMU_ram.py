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
    from pynput.mouse import Controller as MouseController
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pynput", "pystray", "Pillow"])
    from pynput import mouse, keyboard
    import pystray
    from PIL import Image
    from pynput.mouse import Controller as MouseController

# ------------------------
# Configuration
# ------------------------
active = True
left_pressed = False
right_pressed = False
running = True
tick_ms = 20  # small delay between moves
vertical_strength = 6  # constant pull (set to 8x)

mouse_controller = MouseController()

# ------------------------
# Vertical movement loop
# ------------------------
def vertical_loop():
    global left_pressed, right_pressed, active, running
    while running:
        if active and left_pressed and right_pressed:
            mouse_controller.move(0, vertical_strength)
            time.sleep(tick_ms / 1000.0)
        else:
            time.sleep(0.01)

threading.Thread(target=vertical_loop, daemon=True).start()

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
    try:
        if key == keyboard.Key.f9:
            active = not active
        elif key == keyboard.Key.esc:
            running = False
            icon.stop()
            return False
    except AttributeError:
        pass

keyboard.Listener(on_press=on_press).start()

# ------------------------
# System tray
# ------------------------
icon_image = Image.new('RGB', (64, 64), (50, 50, 50))
icon = pystray.Icon("VerticalConstant", icon_image, "Vertical Constant", menu=pystray.Menu(
    pystray.MenuItem("Exit", lambda icon, item: (setattr(sys.modules[__name__], 'running', False), icon.stop()))
))
threading.Thread(target=icon.run, daemon=True).start()

# ------------------------
# Keep script alive
# ------------------------
while running:
    time.sleep(0.2)

