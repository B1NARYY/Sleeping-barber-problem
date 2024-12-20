"""
Main entry point for the Barber Simulation.
- Initializes the application controller and console interface.
- Manages the program's lifecycle.
"""

import os
from src.app_controller import AppController
from src.interface import ConsoleUI
from src.utils import close_files, user_print
from src.logger import logger

if __name__ == '__main__':
    try:
        # Determine the correct path to the configuration file
        if os.path.exists('config.json'):
            config_path = 'config.json'  # When running from editor
        elif os.path.exists('src/config.json'):
            config_path = 'src/config.json'  # When running from terminal
        else:
            raise FileNotFoundError("Configuration file 'config.json' not found in expected locations.")

        # Initialize the application with the detected configuration file path
        app = AppController(config_path)

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
