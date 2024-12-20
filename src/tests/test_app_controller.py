import pytest
from unittest.mock import MagicMock, patch
from src.app_controller import AppController


@pytest.fixture
def app_controller():
    # Mock Config, aby nevyžadoval skutečný soubor config.json
    with patch("src.app_controller.Config") as MockConfig:
        mock_config = MockConfig.return_value
        mock_config.get.side_effect = lambda key, default=None: {
            "initial_urls": [],
            "keywords": [],
            "max_customers": 10,
            "max_queue_size": 5,
        }.get(key, default)
        return AppController("config.json")


def test_add_customer(app_controller):
    # Vytvoření mockovaného zákazníka
    mock_customer = MagicMock()
    mock_customer.url = "https://www.idnes.cz/"
    mock_customer.keywords_count = {"politika": 1, "sport": 2}
    mock_customer.found_links_count = 5

    # Přidání zákazníka
    app_controller.add_customer(mock_customer)

    # Ověření, že zákazník byl přidán
    assert len(app_controller.customers_info) == 1
    assert app_controller.customers_info[0] == mock_customer

    # Kontrola hodnot zákazníka
    added_customer = app_controller.customers_info[0]
    assert added_customer.url == "https://www.idnes.cz/"
    assert added_customer.keywords_count == {"politika": 1, "sport": 2}
    assert added_customer.found_links_count == 5

def test_store_links(app_controller):
    # Vytvoření seznamu odkazů
    links = ["https://www.idnes.cz/", "https://sport.idnes.cz/"]

    # Uložení odkazů
    app_controller.store_links(links)

    # Ověření, že odkazy byly uloženy
    assert len(app_controller.stored_links) == 2
    assert app_controller.stored_links[0] == "https://www.idnes.cz/"
    assert app_controller.stored_links[1] == "https://sport.idnes.cz/"