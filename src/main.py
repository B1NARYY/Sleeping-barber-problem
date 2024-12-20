"""
Main entry point for the Barber Simulation.
- Initializes the application controller and console interface.
- Manages the program's lifecycle.
"""

from src.app_controller import AppController
from src.interface import ConsoleUI
from src.utils import close_files, user_print
from src.logger import logger

if __name__ == '__main__':
    try:
        # Initialize the application with the configuration file
        app = AppController('src/config.json')

        # Set up the console interface for user interaction
        ui = ConsoleUI(app, logger, user_print)

        # Start the interface
        ui.start()
        ui.join()

        # Log the program termination
        logger.info("Program terminated.")
    finally:
        # Ensure that log files are properly closed
        close_files()
