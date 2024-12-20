import pytest
from unittest.mock import MagicMock, patch
from src.interface import ConsoleUI, HelpCommand, StartCommand, StopCommand, StatusCommand, ExitCommand


@pytest.fixture
def mock_app_controller():
    app_controller = MagicMock()
    app_controller.is_running.return_value = False
    return app_controller


@pytest.fixture
def console_ui(mock_app_controller):
    logger = MagicMock()
    user_print = MagicMock()
    return ConsoleUI(app_controller=mock_app_controller, logger=logger, user_print_fn=user_print)


def test_start_command(console_ui):
    # Test příkazu "start"
    start_command = StartCommand()
    console_ui.app_controller.is_running.return_value = False

    start_command.execute(console_ui)

    # Ověření, že metoda `start` byla volána na app_controller
    console_ui.app_controller.start.assert_called_once()


def test_stop_command(console_ui):
    # Test příkazu "stop"
    stop_command = StopCommand()
    console_ui.app_controller.is_running.return_value = True

    stop_command.execute(console_ui)

    # Ověření, že metoda `stop` byla volána na app_controller
    console_ui.app_controller.stop.assert_called_once()




def test_exit_command(console_ui):
    # Test příkazu "exit"
    exit_command = ExitCommand()

    exit_command.execute(console_ui)

    # Ověření, že metoda `stop` byla volána a aplikace ukončena
    console_ui.app_controller.stop.assert_called_once()
    assert console_ui.running is False
