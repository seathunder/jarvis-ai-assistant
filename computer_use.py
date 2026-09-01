import os
import tempfile
from config import logger

# Lazy load pyautogui
def get_pyautogui():
    try:
        import pyautogui
        pyautogui.FAILSAFE = True
        return pyautogui
    except Exception as e:
        logger.error(f"Failed to load pyautogui: {e}")
        return None

def take_desktop_screenshot():
    """
    Takes a desktop screenshot and saves it to a temporary file path.
    """
    pag = get_pyautogui()
    if not pag:
        return None
    try:
        temp_dir = tempfile.gettempdir()
        screenshot_path = os.path.join(temp_dir, "jarvis_screenshot.png")
        screenshot = pag.screenshot()
        screenshot.save(screenshot_path)
        logger.info(f"Screenshot captured at: {screenshot_path}")
        return screenshot_path
    except Exception as e:
        logger.error(f"Error taking screenshot: {e}")
        return None

def move_and_click(x, y):
    """
    Moves mouse cursor to (x, y) and performs a click.
    """
    pag = get_pyautogui()
    if not pag:
        return False
    try:
        pag.moveTo(x, y, duration=0.5)
        pag.click()
        return True
    except Exception as e:
        logger.error(f"Error clicking at ({x}, {y}): {e}")
        return False

def type_text(text_str):
    """
    Types text via native OS keyboard simulation.
    """
    pag = get_pyautogui()
    if not pag:
        return False
    try:
        pag.write(text_str, interval=0.05)
        return True
    except Exception as e:
        logger.error(f"Error typing text: {e}")
        return False
