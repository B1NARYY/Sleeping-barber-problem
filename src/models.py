# src/models.py

import time
import threading
import requests
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
from logger import logger
import queue
import random
from src.utils import user_print, count_keywords, record_customer


def normalize_url(url):
    """
    Normalizes the URL by:
    - Lowercasing the scheme and hostname.
    - Removing trailing slashes.
    - Removing default ports.

    Args:
        url (str): The URL to normalize.

    Returns:
        str: Normalized URL.
    """
    parsed = urlparse(url)
    scheme = parsed.scheme.lower()
    hostname = parsed.hostname.lower() if parsed.hostname else ''
    port = parsed.port
    # Remove default ports
    if (scheme == 'http' and port == 80) or (scheme == 'https' and port == 443):
        netloc = hostname
    elif port:
        netloc = f"{hostname}:{port}"
    else:
        netloc = hostname
    path = parsed.path.rstrip('/').lower()
    # Remove fragment and query for normalization
    normalized = urlunparse((scheme, netloc, path, '', '', ''))
    return normalized


class URLQueue:
    """
    Thread-safe queue for managing URLs.
    """

    def __init__(self):
        self.q = queue.Queue()

    def put_url(self, url):
        """Adds a URL to the queue."""
        self.q.put(url)

    def get_url(self):
        """Gets a URL from the queue."""
        return self.q.get()

    def empty(self):
        """Checks if the queue is empty."""
        return self.q.empty()

    def size(self):
        """Returns the size of the queue."""
        return self.q.qsize()

    def task_done(self):
        """Marks a task as completed."""
        self.q.task_done()


class Parser:
    """
    Extracts and validates links from HTML content.
    """

    def parse(self, html, base_url):
        """
        Extracts all valid links from the given HTML content.

        Args:
            html (str): The HTML content.
            base_url (str): The base URL to resolve relative links.

        Returns:
            list: List of valid, normalized URLs.
        """
        soup = BeautifulSoup(html, 'html.parser')
        found = []
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])
            normalized_url = normalize_url(url)
            if self._valid_url(normalized_url):
                found.append(normalized_url)
        return found

    def _valid_url(self, url):
        """
        Checks if the URL uses a valid scheme (http or https).

        Args:
            url (str): The URL to check.

        Returns:
            bool: True if the URL is valid, False otherwise.
        """
        parsed = urlparse(url)
        return parsed.scheme in ['http', 'https']


class PageFetcher:
    """
    Downloads web pages with retry logic.
    """

    def __init__(self, max_retries=3):
        """
        Initializes the PageFetcher.

        Args:
            max_retries (int): Maximum number of retries for a failed request.
        """
        self.max_retries = max_retries
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MyCrawler/1.0"})

    def fetch(self, url):
        """
        Fetches a web page with retries on failure.

        Args:
            url (str): The URL to fetch.

        Returns:
            str: The HTML content if successful, or None if failed.
        """
        attempt = 0
        backoff = 1
        while attempt < self.max_retries:
            try:
                r = self.session.get(url, timeout=5)
                if r.status_code == 200:
                    logger.info(f"Fetched: {url}")
                    return r.text
                elif r.status_code == 429:
                    logger.warning(f"429 Too Many Requests for {url}, waiting {backoff}s before retry")
                    time.sleep(backoff)
                    backoff *= 2
                else:
                    logger.warning(f"URL {url} returned status code {r.status_code}")
                    return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Error fetching URL {url}: {e}")
                attempt += 1
                time.sleep(backoff)
                backoff *= 2
        return None


class Customer:
    """
    Represents a processed customer.
    """

    def __init__(self, url, keywords_count, found_links_count):
        """
        Initializes a customer with their processed data.

        Args:
            url (str): The URL of the customer.
            keywords_count (dict): Keyword counts found on the page.
            found_links_count (int): Number of links found on the page.
        """
        self.url = url
        self.keywords_count = keywords_count
        self.found_links_count = found_links_count

    def __str__(self):
        """String representation of the customer."""
        return f"URL: {self.url}, Keywords: {self.keywords_count}, New Links: {self.found_links_count}"


class Crawler(threading.Thread):
    """
    Simulates the barber, processing customers (URLs) from the queue.
    """

    def __init__(self, url_queue, parser, fetcher, visited, lock, config, keywords, app_controller):
        """
        Initializes the Crawler.

        Args:
            url_queue (URLQueue): Queue of URLs to process.
            parser (Parser): Extracts links from HTML.
            fetcher (PageFetcher): Downloads web pages.
            visited (set): Set of visited URLs.
            lock (threading.Lock): Thread lock for shared data.
            config (Config): Configuration settings.
            keywords (list): List of keywords to count on pages.
            app_controller (AppController): Main app controller.
        """
        super().__init__()
        self.url_queue = url_queue
        self.parser = parser
        self.fetcher = fetcher
        self.visited = visited
        self.lock = lock
        self.config = config
        self.keywords = keywords
        self.app_controller = app_controller
        self.max_customers = self.config.get("max_customers", 10)
        self.barber_delay_range = self.config.get("barber_delay_seconds", [0.5, 1])
        self.max_queue_size = self.config.get("max_queue_size", 5)
        self.running = True
        self.was_sleeping = False

    def random_delay(self, delay_range):
        """Introduces a random delay within the given range."""
        delay = random.uniform(delay_range[0], delay_range[1])
        time.sleep(delay)

    def run(self):
        """
        Main loop for processing customers from the queue.
        Simulates barber behavior (sleeping, waking, processing).
        """
        while self.running:
            if self.url_queue.empty():
                processed = len(self.app_controller.customers_info)
                user_print(f"Barber is sleeping... (processed: {processed}/{self.max_customers})")
                self.was_sleeping = True
                self.random_delay(self.barber_delay_range)

            if self.url_queue.empty():
                if not self.app_controller.is_running():
                    break
                continue

            url = self.url_queue.get_url()
            if url is None or len(self.app_controller.customers_info) >= self.max_customers:
                user_print("Barber is done for the day!")
                self.running = False
                if url is not None:
                    self.url_queue.task_done()
                self.app_controller.running = False
                break

            if self.was_sleeping:
                user_print("Barber wakes up...")
                self.was_sleeping = False

            user_print(f"Barber processes: {url}")
            self.random_delay(self.barber_delay_range)

            html = self.fetcher.fetch(url)
            if html:
                kw_counts = count_keywords(html, self.keywords)
                found_links = self.parser.parse(html, url)
                user_print(f"Barber analyzed page: {kw_counts}, found {len(found_links)} links")

                self.app_controller.store_links(found_links)

                customer = Customer(url, kw_counts, len(found_links))
                self.app_controller.add_customer(customer)
                record_customer(customer)

                processed = len(self.app_controller.customers_info)
                user_print(f"Barber processed customer (processed: {processed}/{self.max_customers})")

            else:
                user_print("Barber tried to serve this customer, but they vanished!")

            self.url_queue.task_done()
            self.random_delay(self.barber_delay_range)


class URLProducer(threading.Thread):
    """
    Generates new customers (URLs) and adds them to the queue.
    """

    def __init__(self, url_queue, config, delay):
        """
        Initializes the URLProducer.

        Args:
            url_queue (URLQueue): Queue for storing URLs.
            config (Config): Configuration settings.
            delay (float): Optional delay between operations.
        """
        super().__init__()
        self.url_queue = url_queue
        self.config = config
        self.running = True
        self.app_controller = None

    def set_app_controller(self, app):
        """Links the producer to the app controller."""
        self.app_controller = app

    def random_delay(self, delay_range):
        """Introduces a random delay within the given range."""
        delay = random.uniform(delay_range[0], delay_range[1])
        time.sleep(delay)

    def run(self):
        """
        Main loop for generating new customers and adding them to the queue.
        """
        while self.running:
            self.random_delay(self.config.get("producer_delay_seconds", [0.2, 0.5]))
            interval = self.config.get("producer_interval", 1)
            time.sleep(interval if interval >= 0 else 1)

            if not self.app_controller.is_running():
                break

            self.app_controller.reload_config()

            enable_wakeup = self.config.get("enable_wakeup_from_stored_urls", True)
            probability = self.config.get("new_customer_probability", 0.9)
            if enable_wakeup:
                with self.app_controller.lock:
                    if self.app_controller.stored_links and random.random() < probability:
                        # Vybereme náhodný odkaz
                        link = random.choice(self.app_controller.stored_links)
                        self.app_controller.stored_links.remove(link)

                        normalized_link = normalize_url(link)
                        if normalized_link and normalized_link not in self.app_controller.visited:
                            if self.url_queue.size() < self.config.get("max_queue_size", 5):
                                self.url_queue.put_url(normalized_link)
                                self.app_controller.visited.add(normalized_link)
                                size = self.url_queue.size()
                                user_print(
                                    f"New customer added to queue (queue: {size}/{self.config.get('max_queue_size', 5)})")
                            else:
                                user_print("Queue is full, cannot add new customer.")
                        else:
                            user_print("Duplicate customer detected, skipping.")
