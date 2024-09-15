import threading

import pystray
from llama_server import kill_process_llama_cpp
from PIL import Image
from utils import load_config


class TrayIcon:
    def __init__(self, app):
        self.config = load_config()

        self.app = app  # Referência à classe principal
        self.tray_icon = None

    def show_tray_icon(self):
        # Função para criar o ícone da bandeja de sistema
        image = Image.open(self.config["screen"]["icon_path"])

        self.tray_icon = pystray.Icon(
            self.config["app_title"],
            image,
            self.config["app_title"],
            menu=self.create_tray_menu(),
        )
        threading.Thread(target=self.tray_icon.run).start()

    def create_tray_menu(self):
        # Cria o menu do ícone na bandeja
        return pystray.Menu(
            pystray.MenuItem("Restaurar", self.restore_window),
            pystray.MenuItem("Sair", self.quit_app),
        )

    def restore_window(self, icon, item):
        # Função para restaurar a janela
        self.app.janela.deiconify()  # Traz a janela de volta
        self.tray_icon.stop()  # Para o ícone da bandeja

    def quit_app(self, icon, item):
        # Função para encerrar o aplicativo
        kill_process_llama_cpp()
        self.tray_icon.stop()  # Para o ícone da bandeja
        self.app.janela.quit()  # Fecha a janela
