import pytest
from src.utils import count_keywords


def test_count_keywords_empty_html():
    # Test prázdného HTML
    html = ""
    keywords = ["politika", "sport"]
    assert count_keywords(html, keywords) == {"politika": 0, "sport": 0}


def test_count_keywords_no_keywords():
    # Test bez klíčových slov
    html = "<html><body>Text bez klíčových slov.</body></html>"
    keywords = []
    assert count_keywords(html, keywords) == {}


def test_count_keywords_found():
    # Test s nalezenými klíčovými slovy
    html = "<html><body>Politika a sport jsou populární. Politika je důležitá.</body></html>"
    keywords = ["politika", "sport"]
    expected = {"politika": 2, "sport": 1}
    assert count_keywords(html, keywords) == expected


def test_count_keywords_case_insensitivity():
    # Test nezávislosti na velikosti písmen
    html = "<html><body>POLITIKA a Sport jsou populární. politika je důležitá.</body></html>"
    keywords = ["politika", "sport"]
    expected = {"politika": 2, "sport": 1}
    assert count_keywords(html, keywords) == expected


def test_count_keywords_no_match():
    # Test bez nalezených shod
    html = "<html><body>Text o počasí.</body></html>"
    keywords = ["politika", "sport"]
    expected = {"politika": 0, "sport": 0}
    assert count_keywords(html, keywords) == expected
