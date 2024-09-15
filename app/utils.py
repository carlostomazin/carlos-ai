import json
import os
import sys

from plyer import notification


def load_config() -> dict:
    if getattr(sys, "frozen", False):
        # Se o script estiver congelado, usa o diretório onde o executável está localizado
        base_path = sys._MEIPASS
    else:
        # Se o script estiver sendo executado diretamente, usa o diretório atual
        base_path = os.path.dirname(__file__)

    config_path = os.path.join(base_path, "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config


def notify(message: str) -> None:
    config = load_config()
    notification.notify(
        title=config["app_title"],
        message=message,
        app_name=config["app_title"],
        timeout=5,
    )
