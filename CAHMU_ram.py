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
mode = 1  # 1 = 12x, 2 = 15x
left_pressed = False
right_pressed = False
running = True
tick_ms = 14  # 14 ms between moves

mode_strengths = {1: 12, 2: 15}  # mode: vertical pull strength

mouse_controller = MouseController()

# ------------------------
# Vertical movement loop
# ------------------------
def vertical_loop():
    global left_pressed, right_pressed, active, running, mode
    while running:
        if active and left_pressed and right_pressed:
            strength = mode_strengths.get(mode, 12)
            mouse_controller.move(0, strength)
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
        print(f"Active toggled: {'ON' if active else 'OFF'}")

mouse.Listener(on_click=on_click).start()

# ------------------------
# Keyboard listener
# ------------------------
def on_press(key):
    global active, running, mode
    try:
        if key == keyboard.Key.f9:
            active = not active
            print(f"Active toggled: {'ON' if active else 'OFF'}")
        elif key == keyboard.Key.f11:
            mode = 2 if mode == 1 else 1  # toggle mode
            print(f"Switched to Mode {mode} ({mode_strengths[mode]}x)")
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
icon = pystray.Icon("VerticalModes", icon_image, "Vertical Modes", menu=pystray.Menu(
    pystray.MenuItem("Exit", lambda icon, item: (setattr(sys.modules[__name__], 'running', False), icon.stop()))
))
threading.Thread(target=icon.run, daemon=True).start()

# ------------------------
# Keep script alive
# ------------------------
print(f"Starting in Mode {mode} ({mode_strengths[mode]}x)")
while running:
    time.sleep(0.2)
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
mode = 1  # 1 = 12x, 2 = 15x
left_pressed = False
right_pressed = False
running = True
tick_ms = 14  # 14 ms between moves

mode_strengths = {1: 12, 2: 15}  # mode: vertical pull strength

mouse_controller = MouseController()

# ------------------------
# Vertical movement loop
# ------------------------
def vertical_loop():
    global left_pressed, right_pressed, active, running, mode
    while running:
        if active and left_pressed and right_pressed:
            strength = mode_strengths.get(mode, 12)
            mouse_controller.move(0, strength)
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
        print(f"Active toggled: {'ON' if active else 'OFF'}")

mouse.Listener(on_click=on_click).start()

# ------------------------
# Keyboard listener
# ------------------------
def on_press(key):
    global active, running, mode
    try:
        if key == keyboard.Key.f9:
            active = not active
            print(f"Active toggled: {'ON' if active else 'OFF'}")
        elif key == keyboard.Key.f11:
            mode = 2 if mode == 1 else 1  # toggle mode
            print(f"Switched to Mode {mode} ({mode_strengths[mode]}x)")
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
icon = pystray.Icon("VerticalModes", icon_image, "Vertical Modes", menu=pystray.Menu(
    pystray.MenuItem("Exit", lambda icon, item: (setattr(sys.modules[__name__], 'running', False), icon.stop()))
))
threading.Thread(target=icon.run, daemon=True).start()

# ------------------------
# Keep script alive
# ------------------------
print(f"Starting in Mode {mode} ({mode_strengths[mode]}x)")
while running:
    time.sleep(0.2)
