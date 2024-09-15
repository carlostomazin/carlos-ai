import threading
import time

import pyperclip
from pynput import keyboard
from pynput.keyboard import Controller, Key
from utils import notify


class InteractionManager:
    def __init__(self, screen):
        self.screen = screen

    def start(self):
        threading.Thread(target=self.start_handler, daemon=True).start()

    def start_handler(self):
        self.controller = Controller()
        self.hotkeys = {
            "<120>": self.on_f9,  # F9
        }
        with keyboard.GlobalHotKeys(self.hotkeys) as h:
            h.join()

    def on_f9(self):
        with self.controller.pressed(Key.ctrl):
            self.controller.tap("c")

        time.sleep(0.1)
        text = pyperclip.paste()
        if not text:
            return

        self.screen.update_context(text)

        notify("Contexto copiado!")
