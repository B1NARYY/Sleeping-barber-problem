import json
import os
from src.utils import user_print

"""
Config class for managing configuration files.
- Implements a singleton pattern to ensure a single instance.
- Handles loading and fallback for main and backup configuration files.
- Provides access to configuration data.
"""


class Config:
    """
    Singleton class to manage the configuration file.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures only one instance of the class exists.
        """
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def load(self, path):
        """
        Loads the main configuration file and sets up a fallback to a backup file.

        Args:
            path (str): Path to the main configuration file.
        """
        self.main_path = path
        self.backup_path = os.path.join(os.path.dirname(path), 'config_backup.json')
        self._load_with_fallback()

    def _load_with_fallback(self):
        """
        Attempts to load the main configuration file. If it fails, it tries the backup file.
        Exits the program if both fail.
        """
        if not self._try_load(self.main_path):
            user_print("Main config invalid, trying backup config...")
            if not self._try_load(self.backup_path):
                user_print("Both main and backup config files are invalid. Exiting.")
                exit(1)

    def _try_load(self, path):
        """
        Tries to load a configuration file and validates its keys.

        Args:
            path (str): Path to the configuration file.

        Returns:
            bool: True if the file is successfully loaded and valid, False otherwise.
        """
        if not os.path.exists(path):
            return False
        try:
            with open(path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)

            # Validate required keys
            required_keys = [
                "initial_urls",
                "barber_delay_seconds",
                "producer_delay_seconds",
                "keywords",
                "max_customers",
                "max_queue_size",
                "enable_wakeup_from_stored_urls",
                "new_customer_probability",
                "producer_interval"
            ]
            for k in required_keys:
                if k not in self.data:
                    return False
            return True
        except (json.JSONDecodeError, IOError):
            return False

    def reload(self):
        """
        Reloads the configuration file. Tries the main file first, then the backup.
        Exits the program if both fail.
        """
        if not self._try_load(self.main_path):
            user_print("Main config invalid during reload, using backup config...")
            if not self._try_load(self.backup_path):
                user_print("Both main and backup config files invalid during reload. Exiting.")
                exit(1)

    def get(self, key, default=None):
        """
        Retrieves a value from the configuration.

        Args:
            key (str): The configuration key to retrieve.
            default: The default value if the key is not found.

        Returns:
            The value associated with the key, or the default value.
        """
        return self.data.get(key, default)
