import pytest
import os
import json
from src.config import Config


@pytest.fixture
def valid_config(tmp_path):
    config_data = {
        "initial_urls": ["https://www.idnes.cz/"],
        "barber_delay_seconds": [0.5, 2],
        "producer_delay_seconds": [0.2, 0.5],
        "keywords": ["politika", "sport", "ekonomika"],
        "max_customers": 10,
        "max_queue_size": 5,
        "enable_wakeup_from_stored_urls": True,
        "new_customer_probability": 0.9,
        "producer_interval": 1,
    }
    config_file = tmp_path / "config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    return config_file


def test_load_valid_config(valid_config):
    config = Config()
    config.load(str(valid_config))
    assert config.get("initial_urls") == ["https://www.idnes.cz/"]
    assert config.get("max_customers") == 10


def test_load_invalid_config(tmp_path):
    invalid_config_file = tmp_path / "config.json"
    with open(invalid_config_file, "w", encoding="utf-8") as f:
        f.write("INVALID JSON")
    config = Config()
    with pytest.raises(SystemExit):  # Ověření ukončení programu
        config.load(str(invalid_config_file))


def test_load_missing_key(tmp_path):
    config_data = {
        "initial_urls": ["https://www.idnes.cz/"],
        # Chybí některé klíče, například 'barber_delay_seconds'
    }
    config_file = tmp_path / "config.json"
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config_data, f)
    config = Config()
    with pytest.raises(SystemExit):  # Ověření ukončení programu
        config.load(str(config_file))
