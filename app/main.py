from interaction_manager import InteractionManager
from llama_server import start_server
from loguru import logger as log
from screen import Screen

log.info("Starting Llama Server")
start_server()

screen = Screen()
interaction_manager = InteractionManager(screen)

log.info("Starting Interaction Manager")
interaction_manager.start()

log.info("Starting Screen")
screen.run()
