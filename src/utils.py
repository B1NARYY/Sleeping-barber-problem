import os
from logger import RUN_DIR_PATH

"""
Utility functions for the Barber Simulation Program:
- Logging for chat and customer activity.
- Keyword counting in HTML.
- Configuration explanation.
"""

# Paths for log files
chat_log_path = os.path.join(RUN_DIR_PATH, "chat.log")
customers_log_path = os.path.join(RUN_DIR_PATH, "customers.log")

# Open log files for writing
chat_log_file = open(chat_log_path, 'w', encoding='utf-8')
customers_log_file = open(customers_log_path, 'w', encoding='utf-8')


def user_print(msg):
    """
    Prints a message to the console and writes it to the chat log file.

    Args:
        msg (str): The message to log and display.
    """
    print(msg)
    chat_log_file.write(msg + "\n")
    chat_log_file.flush()


def print_config_file():
    """
    Reads and logs the contents of the configuration file.
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as file:
        line = "#" * 50
        config_data = file.read()
        user_print(line)
        user_print(config_data)
        user_print(line)


def record_customer(customer):
    """
    Logs customer information to the customer log file.

    Args:
        customer (Customer): Customer object to log.
    """
    customers_log_file.write(str(customer) + "\n")
    customers_log_file.flush()


def count_keywords(html, keywords):
    """
    Counts occurrences of keywords in HTML content.

    Args:
        html (str): HTML content to search.
        keywords (list): List of keywords to count.

    Returns:
        dict: Dictionary with keywords as keys and their counts as values.
    """
    if not keywords:
        return {}
    text = html.lower()
    counts = {kw.lower(): text.count(kw.lower()) for kw in keywords}
    return counts


def close_files():
    """
    Closes all open log files.
    """
    chat_log_file.close()
    customers_log_file.close()


def explain_config():
    """
    Logs and explains the configuration file's structure and purpose.
    """
    user_print("Config file structure:")
    user_print("initial_urls: list of strings - starting URLs")
    user_print("barber_delay_seconds: list of floats - range of delay before fetching a page")
    user_print("producer_delay_seconds: list of floats - range of delay before adding a new URL")
    user_print("keywords: list of strings - keywords to search for in the page")
    user_print("max_customers: int - maximum number of customers to serve")
    user_print("max_queue_size: int - maximum number of URLs in the queue")
    user_print("enable_wakeup_from_stored_urls: bool - whether to add URLs from the stored list")
    user_print("new_customer_probability: float - probability of adding a new customer")
    user_print("producer_interval: int - interval of adding new URLs (negative to disable)")
