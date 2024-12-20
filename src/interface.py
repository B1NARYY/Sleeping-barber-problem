"""
This module handles the console interface for the Barber Simulation.
- Commands allow users to interact with the simulation.
- ConsoleUI manages the main interaction loop.
"""

import sys
import threading
import queue
import json
import os
from colorama import Fore, Style, init
from src.utils import user_print, print_config_file, explain_config

# Initialize colorama for cross-platform compatibility
init(autoreset=True)

class Command:
    """Base class for all commands."""
    def execute(self, ui):
        raise NotImplementedError

class HelpCommand(Command):
    """Displays available commands and their usage."""
    def execute(self, ui):
        print_config_file()
        ui.colored_print("Available commands:", Fore.BLUE)
        ui.colored_print(" help   - show this help message", Fore.GREEN)
        ui.colored_print(" start  - start the barber", Fore.GREEN)
        ui.colored_print(" stop   - stop the barber", Fore.GREEN)
        ui.colored_print(" status - show current status", Fore.GREEN)
        ui.colored_print(" edit   - edit config.json", Fore.GREEN)
        ui.colored_print(" exit   - exit the program", Fore.GREEN)
        ui.colored_print(" explain - explain config file structure", Fore.GREEN)

class StartCommand(Command):
    """Starts the simulation."""
    def execute(self, ui):
        if not ui.app_controller.is_running():
            ui.colored_print("Simulation started successfully.", Fore.GREEN)
            ui.app_controller.start()
        else:
            ui.colored_print("Barber is still working.", Fore.YELLOW)

class StopCommand(Command):
    """Stops the simulation."""
    def execute(self, ui):
        if ui.app_controller.is_running():
            ui.app_controller.stop()
            ui.colored_print("Simulation stopped successfully.", Fore.RED)
        else:
            ui.colored_print("Barber is not working.", Fore.YELLOW)
        ui.show_summary()

class StatusCommand(Command):
    """Displays the current simulation status."""
    def execute(self, ui):
        ui.colored_print(ui.app_controller.status(), Fore.BLUE)

class ExitCommand(Command):
    """Exits the program."""
    def execute(self, ui):
        ui.running = False
        ui.app_controller.stop()
        ui.colored_print("Exiting the program...", Fore.RED)

class EditCommand(Command):
    """Allows editing of the configuration file."""
    def execute(self, ui):
        ui.colored_print("Enter the config key to edit:", Fore.BLUE)
        sys.stdout.write("(Console) ")
        sys.stdout.flush()
        key = sys.stdin.readline().strip()
        if key.lower() == 'cancel':
            ui.colored_print("Edit canceled.", Fore.YELLOW)
            return

        expected_schema = {
            "initial_urls": ("list_str", None),
            "barber_delay_seconds": ("list_float_pair", lambda x: x[0] < x[1] and all(i > 0 for i in x)),
            "producer_delay_seconds": ("list_float_pair", lambda x: x[0] < x[1] and all(i > 0 for i in x)),
            "keywords": ("list_str", None),
            "max_customers": ("int", lambda x: x >= 1),
            "max_queue_size": ("int", lambda x: x >= 1),
            "enable_wakeup_from_stored_urls": ("bool", None),
            "new_customer_probability": ("float", lambda x: 0 <= x <= 1),
            "producer_interval": ("int", lambda x: x >= 0)
        }

        if key not in expected_schema:
            ui.colored_print(f"Unknown key '{key}'. Edit canceled.", Fore.RED)
            return

        value_type, validator = expected_schema[key]

        ui.colored_print(f"Enter the new value for '{key}' (type '{value_type}') or 'cancel' to abort:", Fore.BLUE)
        while True:
            sys.stdout.write("(Console) ")
            sys.stdout.flush()
            value_str = sys.stdin.readline().strip()
            if value_str.lower() == 'cancel':
                ui.colored_print("Edit canceled.", Fore.YELLOW)
                return

            try:
                if value_type == "int":
                    parsed_value = int(value_str)
                elif value_type == "float":
                    parsed_value = float(value_str)
                elif value_type == "bool":
                    parsed_value = value_str.lower() == "true"
                elif value_type == "list_str":
                    parsed_value = json.loads(value_str)
                    if not isinstance(parsed_value, list) or not all(isinstance(s, str) for s in parsed_value):
                        raise ValueError
                elif value_type == "list_float_pair":
                    parsed_value = json.loads(value_str)
                    if not (isinstance(parsed_value, list) and len(parsed_value) == 2 and all(isinstance(x, (int, float)) for x in parsed_value)):
                        raise ValueError
            except (ValueError, json.JSONDecodeError):
                ui.colored_print("Invalid input, please try again.", Fore.RED)
                continue

            if validator and not validator(parsed_value):
                ui.colored_print("Invalid input, please try again.", Fore.RED)
                continue
            break

        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data[key] = parsed_value
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        ui.colored_print(f"Config key '{key}' updated to '{parsed_value}'. Changes apply on next config reload.", Fore.GREEN)

class ExplainCommand(Command):
    """Explains the structure of the configuration file."""
    def execute(self, ui):
        explain_config()

class ConsoleUI(threading.Thread):
    """
    Main class for handling the console interface.
    Provides a command-based interaction system.
    """
    def __init__(self, app_controller, logger, user_print_fn):
        super().__init__()
        self.app_controller = app_controller
        self.logger = logger
        self.user_print = user_print_fn
        self.running = True
        self.command_queue = queue.Queue()

        self.commands = {
            "help": HelpCommand(),
            "start": StartCommand(),
            "stop": StopCommand(),
            "status": StatusCommand(),
            "exit": ExitCommand(),
            "edit": EditCommand(),
            "explain": ExplainCommand()
        }

    def colored_print(self, message, color):
        """Prints a message in the specified color."""
        print(f"{color}{message}{Style.RESET_ALL}")

    def run(self):
        """Starts the main command input loop."""
        self.colored_print("Enter a command (help for usage):", Fore.BLUE)
        while self.running:
            sys.stdout.write("(Console) ")
            sys.stdout.flush()
            try:
                command_input = sys.stdin.readline().strip().lower()
                if command_input:
                    self.handle_command(command_input)
            except UnicodeDecodeError:
                self.colored_print("Invalid input encoding. Please try again.", Fore.RED)
            except KeyboardInterrupt:
                self.colored_print("\nKeyboardInterrupt received. Exiting.", Fore.RED)
                self.running = False
                self.app_controller.stop()

    def handle_command(self, command_input):
        """Handles a user command."""
        cmd = self.commands.get(command_input, None)
        if cmd:
            cmd.execute(self)
        else:
            self.colored_print(f"Unknown command: {command_input}. Type 'help' for usage.", Fore.YELLOW)

    def show_summary(self):
        """Displays a summary of processed customers."""
        self.app_controller.show_customers()
