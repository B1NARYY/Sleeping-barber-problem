import pytest
from src.models import URLQueue


def test_url_queue_initialization():
    # Test inicializace prázdné fronty
    queue = URLQueue()
    assert queue.empty() is True
    assert queue.size() == 0


def test_url_queue_put_and_get():
    # Test přidávání a odebírání URL
    queue = URLQueue()
    queue.put_url("https://www.idnes.cz/")
    queue.put_url("https://sport.idnes.cz/")
    assert queue.empty() is False
    assert queue.size() == 2

    url1 = queue.get_url()
    url2 = queue.get_url()
    assert url1 == "https://www.idnes.cz/"
    assert url2 == "https://sport.idnes.cz/"
    assert queue.empty() is True


def test_url_queue_task_done():
    # Test operace task_done
    queue = URLQueue()
    queue.put_url("https://www.idnes.cz/")
    queue.task_done()  # Task done neovlivňuje velikost fronty
    assert queue.size() == 1
    url = queue.get_url()
    assert url == "https://www.idnes.cz/"
    assert queue.empty() is True


def test_url_queue_multiple_puts():
    # Test přidávání více URL
    queue = URLQueue()
    urls = ["https://www.idnes.cz/", "https://sport.idnes.cz/", "https://ekonomika.idnes.cz/"]
    for url in urls:
        queue.put_url(url)

    assert queue.size() == 3

    for url in urls:
        assert queue.get_url() == url

    assert queue.empty() is True
